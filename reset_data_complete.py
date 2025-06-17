#!/usr/bin/env python3
"""
完整数据重置脚本 - 直接操作所有数据库，包括 chroma.sqlite3
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

def clear_chroma_sqlite(chroma_db_path):
    """直接清理 chroma.sqlite3 数据库"""
    chroma_sqlite_path = os.path.join(chroma_db_path, "chroma.sqlite3")
    
    if not os.path.exists(chroma_sqlite_path):
        logger.info("chroma.sqlite3 不存在，跳过清理")
        return True
    
    try:
        with sqlite3.connect(chroma_sqlite_path) as conn:
            # 获取所有表名
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"发现 ChromaDB 表: {tables}")
            
            # 清空所有数据表（保留表结构）
            tables_to_clear = []
            for table in tables:
                if table != 'sqlite_sequence':  # 保留系统表
                    try:
                        cursor = conn.execute(f"DELETE FROM {table}")
                        deleted_count = cursor.rowcount
                        tables_to_clear.append(f"{table}({deleted_count})")
                    except Exception as e:
                        logger.warning(f"清空表 {table} 失败: {e}")
            
            conn.commit()
            logger.info(f"✅ chroma.sqlite3: 清空了表 {', '.join(tables_to_clear)}")
            
            # 重置自增序列
            try:
                conn.execute("DELETE FROM sqlite_sequence")
                conn.commit()
                logger.info("✅ 重置了自增序列")
            except Exception:
                pass  # sqlite_sequence 可能不存在
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 清理 chroma.sqlite3 失败: {e}")
        return False

def clear_chroma_vector_files(chroma_db_path):
    """清理 ChromaDB 向量文件"""
    try:
        deleted_dirs = []
        for item in os.listdir(chroma_db_path):
            item_path = os.path.join(chroma_db_path, item)
            if os.path.isdir(item_path) and item != "__pycache__":
                try:
                    shutil.rmtree(item_path)
                    deleted_dirs.append(item)
                except Exception as e:
                    logger.warning(f"删除向量目录 {item} 失败: {e}")
        
        if deleted_dirs:
            logger.info(f"✅ 删除了向量目录: {', '.join(deleted_dirs)}")
        else:
            logger.info("没有找到需要删除的向量目录")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 清理向量文件失败: {e}")
        return False

def clear_document_data_complete(storage_dir="storage"):
    """完整清空文档数据，包括直接操作 chroma.sqlite3"""
    logger.info("🔄 开始完整清空文档数据...")
    
    # 1. 清空SQLite数据库中的文档数据
    docstore_path = os.path.join(storage_dir, "docstore.db")
    if os.path.exists(docstore_path):
        try:
            with sqlite3.connect(docstore_path) as conn:
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
    
    # 3. 直接清理 ChromaDB SQLite 数据库
    chroma_db_path = os.path.join(storage_dir, "chroma_db")
    if os.path.exists(chroma_db_path):
        if not clear_chroma_sqlite(chroma_db_path):
            return False
        
        # 4. 清理向量文件
        if not clear_chroma_vector_files(chroma_db_path):
            return False
    
    # 5. 清空data目录中的文档文件
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
                        pass
            
            logger.info(f"✅ data目录: 删除了 {file_count} 个文档文件")
        except Exception as e:
            logger.error(f"❌ 清空data目录失败: {e}")
            return False
    
    return True

def verify_complete_reset(storage_dir="storage"):
    """验证完整重置结果"""
    logger.info("🔍 验证完整重置结果...")
    
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
    
    # 检查chroma.sqlite3
    chroma_sqlite_path = os.path.join(storage_dir, "chroma_db", "chroma.sqlite3")
    if os.path.exists(chroma_sqlite_path):
        try:
            with sqlite3.connect(chroma_sqlite_path) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                table_counts = []
                for table in tables:
                    if table != 'sqlite_sequence':
                        try:
                            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                            count = cursor.fetchone()[0]
                            table_counts.append(f"{table}({count})")
                        except Exception:
                            pass
                
                logger.info(f"📊 chroma.sqlite3: {', '.join(table_counts)}")
        except Exception as e:
            logger.warning(f"⚠️  无法检查chroma.sqlite3: {e}")
    
    # 检查data目录
    data_dir = os.environ.get("DATA_DIR", "data")
    if os.path.exists(data_dir):
        file_count = sum(len(files) for _, _, files in os.walk(data_dir))
        logger.info(f"📊 data目录: {file_count} 个文件")
    
    logger.info("✅ 完整重置验证完成")

def main():
    """主重置流程"""
    storage_dir = "storage"
    
    print("🔄 开始完整数据重置（包括 chroma.sqlite3）")
    print("=" * 60)
    
    # 1. 完整清空文档数据
    if not clear_document_data_complete(storage_dir):
        print("❌ 完整数据重置失败")
        return
    
    # 2. 验证重置结果
    verify_complete_reset(storage_dir)
    
    print()
    print("🎉 完整数据重置完成！")
    print("=" * 60)
    print("✅ 已清空所有文档数据（包括 chroma.sqlite3）")
    print("✅ 保留了数据库表结构和配置")
    print("✅ 清理了所有向量文件")
    print("🚀 现在可以重新上传文档")

if __name__ == "__main__":
    main()
