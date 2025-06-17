#!/usr/bin/env python3
"""
数据重置脚本 - 只删除文档数据，保留配置和表结构
"""
import os
import shutil
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clear_document_data(storage_dir="storage"):
    """清空文档数据，保留配置和表结构"""
    logger.info("🔄 开始清空文档数据...")
    
    # 1. 清空SQLite数据库中的文档数据
    docstore_path = os.path.join(storage_dir, "docstore.db")
    if os.path.exists(docstore_path):
        try:
            with sqlite3.connect(docstore_path) as conn:
                # 清空文档相关表的数据，但保留表结构
                cursor = conn.execute("DELETE FROM documents")
                docs_deleted = cursor.rowcount
                
                cursor = conn.execute("DELETE FROM ref_doc_info")
                refs_deleted = cursor.rowcount
                
                cursor = conn.execute("DELETE FROM files")
                files_deleted = cursor.rowcount
                
                conn.commit()
                logger.info(f"✅ docstore.db: 删除了 {docs_deleted} 个文档, {refs_deleted} 个引用, {files_deleted} 个文件记录")
        except Exception as e:
            logger.error(f"❌ 清空docstore.db失败: {e}")
            return False
    
    # 2. 清空索引存储中的数据
    index_store_path = os.path.join(storage_dir, "index_store.db")
    if os.path.exists(index_store_path):
        try:
            with sqlite3.connect(index_store_path) as conn:
                cursor = conn.execute("DELETE FROM index_structs")
                indexes_deleted = cursor.rowcount
                conn.commit()
                logger.info(f"✅ index_store.db: 删除了 {indexes_deleted} 个索引结构")
        except Exception as e:
            logger.error(f"❌ 清空index_store.db失败: {e}")
            return False
    
    # 3. 重置ChromaDB向量数据
    chroma_db_path = os.path.join(storage_dir, "chroma_db")
    if os.path.exists(chroma_db_path):
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            # 创建ChromaDB客户端
            chroma_client = chromadb.PersistentClient(
                path=chroma_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 删除现有集合并重新创建
            collection_name = "document_vectors"
            try:
                chroma_client.delete_collection(collection_name)
                logger.info(f"✅ 删除了ChromaDB集合: {collection_name}")
            except Exception:
                logger.info(f"ChromaDB集合 {collection_name} 不存在，跳过删除")
            
            # 重新创建空集合
            chroma_client.create_collection(collection_name)
            logger.info(f"✅ 重新创建了ChromaDB集合: {collection_name}")
            
        except Exception as e:
            logger.error(f"❌ 重置ChromaDB失败: {e}")
            return False
    
    # 4. 清空data目录中的文档文件
    data_dir = os.environ.get("DATA_DIR", "data")
    if os.path.exists(data_dir):
        try:
            file_count = 0
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    file_count += 1
            
            # 删除空目录（保留根目录）
            for root, dirs, files in os.walk(data_dir, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        os.rmdir(dir_path)
                    except OSError:
                        pass  # 目录不为空，忽略
            
            logger.info(f"✅ data目录: 删除了 {file_count} 个文档文件")
        except Exception as e:
            logger.error(f"❌ 清空data目录失败: {e}")
            return False
    
    return True

def verify_data_reset(storage_dir="storage"):
    """验证数据重置结果"""
    logger.info("🔍 验证数据重置结果...")
    
    # 检查docstore.db
    docstore_path = os.path.join(storage_dir, "docstore.db")
    if os.path.exists(docstore_path):
        with sqlite3.connect(docstore_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM documents")
            doc_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM files")
            file_count = cursor.fetchone()[0]
            
            logger.info(f"📊 docstore.db: {doc_count} 个文档, {file_count} 个文件记录")
    
    # 检查index_store.db
    index_store_path = os.path.join(storage_dir, "index_store.db")
    if os.path.exists(index_store_path):
        with sqlite3.connect(index_store_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM index_structs")
            index_count = cursor.fetchone()[0]
            logger.info(f"📊 index_store.db: {index_count} 个索引结构")
    
    # 检查ChromaDB
    chroma_db_path = os.path.join(storage_dir, "chroma_db")
    if os.path.exists(chroma_db_path):
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            chroma_client = chromadb.PersistentClient(
                path=chroma_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            collection = chroma_client.get_collection("document_vectors")
            vector_count = collection.count()
            logger.info(f"📊 ChromaDB: {vector_count} 个向量")
        except Exception as e:
            logger.warning(f"⚠️  无法检查ChromaDB: {e}")
    
    # 检查data目录
    data_dir = os.environ.get("DATA_DIR", "data")
    if os.path.exists(data_dir):
        file_count = sum(len(files) for _, _, files in os.walk(data_dir))
        logger.info(f"📊 data目录: {file_count} 个文件")
    
    logger.info("✅ 数据重置验证完成")

def main():
    """主重置流程"""
    storage_dir = "storage"
    
    print("🔄 开始数据重置（保留配置）")
    print("=" * 50)
    
    # 1. 清空文档数据
    if not clear_document_data(storage_dir):
        print("❌ 数据重置失败")
        return
    
    # 2. 验证重置结果
    verify_data_reset(storage_dir)
    
    print()
    print("🎉 数据重置完成！")
    print("=" * 50)
    print("✅ 已清空所有文档数据")
    print("✅ 保留了数据库表结构和配置")
    print("✅ 保留了ChromaDB集合结构")
    print("🚀 现在可以重新上传文档")

if __name__ == "__main__":
    main()
