#!/usr/bin/env python3
"""
测试存储配置的脚本
"""
import os
import logging
import traceback

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_storage_creation():
    """测试存储上下文创建"""
    try:
        logger.info("开始测试存储上下文创建...")
        
        # 导入必要的模块
        from app.storage_config import get_storage_context
        from app.index import STORAGE_DIR
        
        logger.info(f"存储目录: {STORAGE_DIR}")
        
        # 尝试创建存储上下文
        storage_context = get_storage_context(STORAGE_DIR)
        
        logger.info("✅ 存储上下文创建成功！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 存储上下文创建失败: {e}")
        logger.error(f"详细错误信息:\n{traceback.format_exc()}")
        return False

def test_chromadb_directly():
    """直接测试 ChromaDB"""
    try:
        logger.info("开始直接测试 ChromaDB...")
        
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        chroma_db_path = os.path.join("storage", "chroma_db")
        logger.info(f"ChromaDB 路径: {chroma_db_path}")
        
        # 创建 ChromaDB 客户端
        chroma_client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        logger.info("✅ ChromaDB 客户端创建成功！")
        
        # 尝试创建集合
        collection_name = "test_collection"
        try:
            collection = chroma_client.get_collection(collection_name)
            logger.info(f"找到现有集合: {collection_name}")
        except Exception:
            collection = chroma_client.create_collection(collection_name)
            logger.info(f"创建新集合: {collection_name}")
        
        logger.info("✅ ChromaDB 集合操作成功！")
        return True
        
    except Exception as e:
        logger.error(f"❌ ChromaDB 测试失败: {e}")
        logger.error(f"详细错误信息:\n{traceback.format_exc()}")
        return False

def test_sqlite_stores():
    """测试 SQLite 存储"""
    try:
        logger.info("开始测试 SQLite 存储...")
        
        from app.sqlite_stores import SQLiteDocumentStore, SQLiteIndexStore
        
        # 测试文档存储
        docstore_path = os.path.join("storage", "docstore.db")
        docstore = SQLiteDocumentStore(docstore_path)
        logger.info("✅ SQLite 文档存储创建成功！")
        
        # 测试索引存储
        index_store_path = os.path.join("storage", "index_store.db")
        index_store = SQLiteIndexStore(index_store_path)
        logger.info("✅ SQLite 索引存储创建成功！")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SQLite 存储测试失败: {e}")
        logger.error(f"详细错误信息:\n{traceback.format_exc()}")
        return False

def main():
    """主测试流程"""
    print("🔍 开始存储系统诊断")
    print("=" * 50)
    
    # 1. 测试 SQLite 存储
    if test_sqlite_stores():
        print("✅ SQLite 存储测试通过")
    else:
        print("❌ SQLite 存储测试失败")
    
    print()
    
    # 2. 测试 ChromaDB
    if test_chromadb_directly():
        print("✅ ChromaDB 测试通过")
    else:
        print("❌ ChromaDB 测试失败")
    
    print()
    
    # 3. 测试完整存储上下文
    if test_storage_creation():
        print("✅ 存储上下文测试通过")
    else:
        print("❌ 存储上下文测试失败")
    
    print()
    print("🎉 诊断完成！")

if __name__ == "__main__":
    main()
