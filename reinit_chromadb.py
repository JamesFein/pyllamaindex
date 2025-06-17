#!/usr/bin/env python3
"""
重新初始化 ChromaDB 数据库 - 不删除文件，直接重置数据
"""
import os
import sqlite3
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_chromadb_database():
    """重置 ChromaDB 数据库内容"""
    chroma_sqlite_path = os.path.join("storage", "chroma_db", "chroma.sqlite3")
    
    if not os.path.exists(chroma_sqlite_path):
        logger.info("chroma.sqlite3 不存在")
        return True
    
    try:
        with sqlite3.connect(chroma_sqlite_path) as conn:
            logger.info("🔧 重置 ChromaDB 数据库...")
            
            # 删除所有数据但保留表结构
            tables_to_clear = [
                'embeddings', 'embedding_metadata', 'collections', 
                'segments', 'segment_metadata', 'collection_metadata'
            ]
            
            for table in tables_to_clear:
                try:
                    cursor = conn.execute(f"DELETE FROM {table}")
                    deleted = cursor.rowcount
                    logger.info(f"清空表 {table}: {deleted} 行")
                except Exception as e:
                    logger.warning(f"清空表 {table} 失败: {e}")
            
            # 重置序列
            try:
                conn.execute("DELETE FROM sqlite_sequence")
                logger.info("重置自增序列")
            except Exception:
                pass
            
            # 确保有默认租户和数据库
            try:
                # 检查并插入默认租户
                cursor = conn.execute("SELECT COUNT(*) FROM tenants WHERE name = 'default_tenant'")
                if cursor.fetchone()[0] == 0:
                    conn.execute("""
                        INSERT INTO tenants (id, name) 
                        VALUES ('default_tenant_id', 'default_tenant')
                    """)
                    logger.info("插入默认租户")
                
                # 检查并插入默认数据库
                cursor = conn.execute("SELECT COUNT(*) FROM databases WHERE name = 'default_database'")
                if cursor.fetchone()[0] == 0:
                    conn.execute("""
                        INSERT INTO databases (id, name, tenant_id) 
                        VALUES ('default_database_id', 'default_database', 'default_tenant_id')
                    """)
                    logger.info("插入默认数据库")
                
            except Exception as e:
                logger.warning(f"插入默认数据失败: {e}")
            
            conn.commit()
            logger.info("✅ ChromaDB 数据库重置完成")
            return True
            
    except Exception as e:
        logger.error(f"❌ 重置 ChromaDB 数据库失败: {e}")
        return False

def test_chromadb_connection():
    """测试 ChromaDB 连接"""
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        logger.info("🔍 测试 ChromaDB 连接...")
        
        chroma_db_path = os.path.join("storage", "chroma_db")
        
        # 创建客户端
        chroma_client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        logger.info("✅ ChromaDB 客户端创建成功")
        
        # 创建或获取集合
        collection_name = "document_vectors"
        try:
            collection = chroma_client.get_collection(collection_name)
            logger.info(f"找到现有集合: {collection_name}")
        except Exception:
            collection = chroma_client.create_collection(collection_name)
            logger.info(f"创建新集合: {collection_name}")
        
        count = collection.count()
        logger.info(f"✅ 集合 {collection_name} 包含 {count} 个向量")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ChromaDB 连接测试失败: {e}")
        return False

def test_storage_context():
    """测试存储上下文"""
    try:
        from app.storage_config import get_storage_context
        
        logger.info("🔧 测试存储上下文...")
        storage_context = get_storage_context("storage")
        logger.info("✅ 存储上下文创建成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 存储上下文测试失败: {e}")
        return False

def test_generate_command():
    """测试 generate 命令的核心逻辑"""
    try:
        from app.index import STORAGE_DIR
        from app.settings import init_settings
        from app.storage_config import get_storage_context
        from llama_index.core.readers import SimpleDirectoryReader
        from dotenv import load_dotenv
        
        logger.info("🔧 测试 generate 命令核心逻辑...")
        
        load_dotenv()
        init_settings()
        
        # 创建存储上下文
        storage_context = get_storage_context(STORAGE_DIR)
        logger.info("✅ 存储上下文创建成功")
        
        # 测试文档读取
        data_dir = os.environ.get("DATA_DIR", "data")
        reader = SimpleDirectoryReader(data_dir, recursive=True)
        documents = reader.load_data()
        logger.info(f"✅ 成功读取 {len(documents)} 个文档")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ generate 命令测试失败: {e}")
        return False

def main():
    """主修复流程"""
    print("🔧 开始重新初始化 ChromaDB")
    print("=" * 50)
    
    # 1. 重置 ChromaDB 数据库
    if not reset_chromadb_database():
        print("❌ 修复失败：无法重置 ChromaDB 数据库")
        return
    
    # 2. 测试 ChromaDB 连接
    if not test_chromadb_connection():
        print("❌ 修复失败：ChromaDB 连接测试失败")
        return
    
    # 3. 测试存储上下文
    if not test_storage_context():
        print("❌ 修复失败：存储上下文测试失败")
        return
    
    # 4. 测试 generate 命令核心逻辑
    if not test_generate_command():
        print("❌ 修复失败：generate 命令测试失败")
        return
    
    print()
    print("🎉 ChromaDB 重新初始化完成！")
    print("=" * 50)
    print("✅ ChromaDB 数据库已重置")
    print("✅ ChromaDB 连接测试通过")
    print("✅ 存储上下文测试通过")
    print("✅ generate 命令核心逻辑测试通过")
    print()
    print("🚀 现在可以运行 'uv run generate' 命令了")

if __name__ == "__main__":
    main()
