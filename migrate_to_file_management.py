#!/usr/bin/env python3
"""
数据库迁移脚本：从文本块管理迁移到正确的文件管理结构
"""

import sqlite3
import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_file_hash(file_path: str) -> str:
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.warning(f"Failed to calculate hash for {file_path}: {e}")
        return ""

def migrate_database():
    """执行数据库迁移"""
    db_path = "storage/docstore.db"
    data_dir = "data"
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return False
    
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            # 1. 创建新的files表
            logger.info("Creating files table...")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    file_id TEXT PRIMARY KEY,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_type TEXT NOT NULL,
                    file_hash TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. 为documents表添加新列
            logger.info("Adding new columns to documents table...")
            try:
                conn.execute("ALTER TABLE documents ADD COLUMN file_id TEXT")
                logger.info("Added file_id column")
            except sqlite3.OperationalError:
                logger.info("file_id column already exists")
            
            try:
                conn.execute("ALTER TABLE documents ADD COLUMN chunk_index INTEGER")
                logger.info("Added chunk_index column")
            except sqlite3.OperationalError:
                logger.info("chunk_index column already exists")
            
            # 3. 创建索引
            logger.info("Creating indexes...")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_upload_date ON files(upload_date DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_name ON files(file_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_file_id ON documents(file_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_chunk_index ON documents(file_id, chunk_index)")
            
            # 4. 分析现有数据，按文件名分组
            logger.info("Analyzing existing documents...")
            cursor = conn.execute("""
                SELECT doc_id, data, file_name, file_size, file_type, upload_date, created_at
                FROM documents 
                WHERE file_name IS NOT NULL
                ORDER BY file_name, created_at
            """)
            documents = cursor.fetchall()
            
            # 按文件名分组文档
            files_data = {}
            for doc_id, data, file_name, file_size, file_type, upload_date, created_at in documents:
                if file_name not in files_data:
                    files_data[file_name] = {
                        'chunks': [],
                        'file_size': file_size,
                        'file_type': file_type,
                        'upload_date': upload_date,
                        'created_at': created_at
                    }
                files_data[file_name]['chunks'].append({
                    'doc_id': doc_id,
                    'data': data
                })
            
            logger.info(f"Found {len(files_data)} unique files with {len(documents)} total chunks")
            
            # 5. 为每个文件创建记录
            file_id_mapping = {}  # file_name -> file_id
            
            for file_name, file_info in files_data.items():
                # 生成文件ID
                file_id = f"file_{hashlib.md5(file_name.encode()).hexdigest()[:8]}"
                file_id_mapping[file_name] = file_id
                
                # 查找实际文件路径
                file_path = None
                for data_file in Path(data_dir).rglob("*"):
                    if data_file.is_file() and data_file.name == file_name:
                        file_path = str(data_file)
                        break
                
                if not file_path:
                    # 如果找不到原文件，使用虚拟路径
                    file_path = f"{data_dir}/{file_name}"
                    logger.warning(f"Original file not found for {file_name}, using virtual path")
                
                # 计算文件哈希
                file_hash = calculate_file_hash(file_path) if os.path.exists(file_path) else ""
                
                # 插入files表
                conn.execute("""
                    INSERT OR REPLACE INTO files 
                    (file_id, file_name, file_path, file_size, file_type, file_hash, upload_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id, file_name, file_path, 
                    file_info['file_size'] or 0, 
                    file_info['file_type'] or 'text/plain',
                    file_hash,
                    file_info['upload_date'], 
                    file_info['created_at'], 
                    file_info['upload_date']
                ))
                
                # 更新documents表，添加file_id和chunk_index
                for chunk_index, chunk in enumerate(file_info['chunks']):
                    conn.execute("""
                        UPDATE documents 
                        SET file_id = ?, chunk_index = ?
                        WHERE doc_id = ?
                    """, (file_id, chunk_index + 1, chunk['doc_id']))
                
                logger.info(f"Processed file {file_name} -> {file_id} with {len(file_info['chunks'])} chunks")
            
            # 6. 处理没有file_name的文档（设为孤立文档）
            cursor = conn.execute("SELECT COUNT(*) FROM documents WHERE file_name IS NULL")
            orphan_count = cursor.fetchone()[0]
            
            if orphan_count > 0:
                logger.info(f"Found {orphan_count} orphan documents without file_name")
                # 可以选择删除或者创建虚拟文件记录
                # 这里我们创建一个特殊的"未知文档"记录
                unknown_file_id = "file_unknown"
                conn.execute("""
                    INSERT OR REPLACE INTO files 
                    (file_id, file_name, file_path, file_size, file_type, file_hash, upload_date)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (unknown_file_id, "未知文档.txt", "data/unknown.txt", 0, "text/plain", ""))
                
                # 更新孤立文档
                conn.execute("""
                    UPDATE documents 
                    SET file_id = ?, chunk_index = 1
                    WHERE file_name IS NULL
                """)
            
            conn.commit()
            
            # 7. 验证迁移结果
            cursor = conn.execute("SELECT COUNT(*) FROM files")
            files_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM documents WHERE file_id IS NOT NULL")
            linked_docs_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM documents")
            total_docs_count = cursor.fetchone()[0]
            
            logger.info(f"Migration completed:")
            logger.info(f"  - Created {files_count} file records")
            logger.info(f"  - Linked {linked_docs_count}/{total_docs_count} document chunks")
            
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    if success:
        logger.info("✅ Database migration completed successfully!")
    else:
        logger.error("❌ Database migration failed!")
