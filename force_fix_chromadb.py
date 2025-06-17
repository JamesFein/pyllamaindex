#!/usr/bin/env python3
"""
强制修复 ChromaDB 数据库状态的脚本 - 使用重命名方式绕过文件占用
"""
import os
import shutil
import sqlite3
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def force_move_chromadb(chroma_db_path):
    """强制移动 ChromaDB 目录（绕过文件占用）"""
    if not os.path.exists(chroma_db_path):
        logger.info("ChromaDB 目录不存在")
        return True
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_path = f"{chroma_db_path}_old_{timestamp}"
    
    try:
        # 尝试重命名目录
        os.rename(chroma_db_path, temp_path)
        logger.info(f"✅ 已将 ChromaDB 目录重命名为: {temp_path}")
        return True
    except Exception as e:
        logger.error(f"❌ 重命名 ChromaDB 目录失败: {e}")
        return False

def create_fresh_chromadb_simple(chroma_db_path):
    """创建全新的 ChromaDB（简化版）"""
    try:
        logger.info("🔧 创建全新的 ChromaDB...")
        
        # 确保目录存在
        os.makedirs(chroma_db_path, exist_ok=True)
        
        # 创建一个简单的 SQLite 数据库文件
        chroma_sqlite_path = os.path.join(chroma_db_path, "chroma.sqlite3")
        
        # 创建基本的数据库结构
        with sqlite3.connect(chroma_sqlite_path) as conn:
            # 创建基本表结构（最小化版本）
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tenants (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS databases (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collections (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    database_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (database_id) REFERENCES databases(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id TEXT PRIMARY KEY,
                    collection_id TEXT NOT NULL,
                    embedding BLOB,
                    document TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (collection_id) REFERENCES collections(id)
                )
            """)
            
            # 插入默认租户和数据库
            conn.execute("""
                INSERT OR IGNORE INTO tenants (id, name) 
                VALUES ('default_tenant_id', 'default_tenant')
            """)
            
            conn.execute("""
                INSERT OR IGNORE INTO databases (id, name, tenant_id) 
                VALUES ('default_database_id', 'default_database', 'default_tenant_id')
            """)
            
            conn.commit()
        
        logger.info(f"✅ 创建了基本的 ChromaDB 结构: {chroma_sqlite_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建 ChromaDB 失败: {e}")
        return False

def test_chromadb_with_retry(chroma_db_path):
    """测试 ChromaDB 连接（带重试）"""
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        logger.info("🔍 测试 ChromaDB 连接...")
        
        # 创建 ChromaDB 客户端
        chroma_client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 尝试创建集合
        collection_name = "document_vectors"
        try:
            collection = chroma_client.get_collection(collection_name)
            logger.info(f"找到现有集合: {collection_name}")
        except Exception:
            collection = chroma_client.create_collection(collection_name)
            logger.info(f"创建新集合: {collection_name}")
        
        count = collection.count()
        logger.info(f"✅ ChromaDB 测试成功，集合包含 {count} 个向量")
        return True
        
    except Exception as e:
        logger.error(f"❌ ChromaDB 测试失败: {e}")
        return False

def test_full_storage_context():
    """测试完整的存储上下文"""
    try:
        from app.storage_config import get_storage_context
        
        logger.info("🔧 测试完整存储上下文...")
        storage_context = get_storage_context("storage")
        logger.info("✅ 完整存储上下文创建成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 完整存储上下文测试失败: {e}")
        return False

def main():
    """主修复流程"""
    storage_dir = "storage"
    chroma_db_path = os.path.join(storage_dir, "chroma_db")
    
    print("🔧 开始强制修复 ChromaDB")
    print("=" * 50)
    
    # 1. 强制移动现有的 ChromaDB 目录
    if not force_move_chromadb(chroma_db_path):
        print("❌ 修复失败：无法移动现有 ChromaDB")
        return
    
    # 2. 创建简化的 ChromaDB 结构
    if not create_fresh_chromadb_simple(chroma_db_path):
        print("❌ 修复失败：无法创建新的 ChromaDB")
        return
    
    # 3. 测试 ChromaDB 连接
    if not test_chromadb_with_retry(chroma_db_path):
        print("❌ 修复失败：ChromaDB 连接测试失败")
        return
    
    # 4. 测试完整存储上下文
    if not test_full_storage_context():
        print("❌ 修复失败：完整存储上下文测试失败")
        return
    
    print()
    print("🎉 ChromaDB 强制修复完成！")
    print("=" * 50)
    print("✅ 已创建全新的 ChromaDB")
    print("✅ ChromaDB 连接测试通过")
    print("✅ 完整存储上下文测试通过")
    print()
    print("🚀 现在可以运行 generate 命令了")

if __name__ == "__main__":
    main()
