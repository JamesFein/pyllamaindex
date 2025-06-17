#!/usr/bin/env python3
"""
修复 ChromaDB 迁移状态的脚本
"""
import os
import sqlite3
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_chromadb_migrations():
    """修复 ChromaDB 迁移状态"""
    chroma_sqlite_path = os.path.join("storage", "chroma_db", "chroma.sqlite3")
    
    if not os.path.exists(chroma_sqlite_path):
        logger.info("chroma.sqlite3 不存在")
        return True
    
    try:
        with sqlite3.connect(chroma_sqlite_path) as conn:
            logger.info("🔧 修复 ChromaDB 迁移状态...")
            
            # 检查 migrations 表
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
            if cursor.fetchone():
                # 清空 migrations 表，让 ChromaDB 重新运行迁移
                conn.execute("DELETE FROM migrations")
                logger.info("清空 migrations 表")
            
            # 删除可能导致冲突的表
            tables_to_drop = [
                'embeddings_queue', 'embeddings_queue_config'
            ]
            
            for table in tables_to_drop:
                try:
                    conn.execute(f"DROP TABLE IF EXISTS {table}")
                    logger.info(f"删除表: {table}")
                except Exception as e:
                    logger.warning(f"删除表 {table} 失败: {e}")
            
            conn.commit()
            logger.info("✅ ChromaDB 迁移状态修复完成")
            return True
            
    except Exception as e:
        logger.error(f"❌ 修复 ChromaDB 迁移状态失败: {e}")
        return False

def test_chromadb_after_fix():
    """修复后测试 ChromaDB"""
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        logger.info("🔍 测试修复后的 ChromaDB...")
        
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
        
        # 创建集合
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
        logger.error(f"❌ 修复后 ChromaDB 测试失败: {e}")
        return False

def test_full_workflow():
    """测试完整工作流"""
    try:
        from app.storage_config import get_storage_context
        
        logger.info("🔧 测试完整工作流...")
        
        # 测试存储上下文
        storage_context = get_storage_context("storage")
        logger.info("✅ 存储上下文创建成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 完整工作流测试失败: {e}")
        return False

def main():
    """主修复流程"""
    print("🔧 开始修复 ChromaDB 迁移状态")
    print("=" * 50)
    
    # 1. 修复 ChromaDB 迁移状态
    if not fix_chromadb_migrations():
        print("❌ 修复失败：无法修复 ChromaDB 迁移状态")
        return
    
    # 2. 测试修复后的 ChromaDB
    if not test_chromadb_after_fix():
        print("❌ 修复失败：修复后 ChromaDB 测试失败")
        return
    
    # 3. 测试完整工作流
    if not test_full_workflow():
        print("❌ 修复失败：完整工作流测试失败")
        return
    
    print()
    print("🎉 ChromaDB 迁移状态修复完成！")
    print("=" * 50)
    print("✅ ChromaDB 迁移状态已修复")
    print("✅ ChromaDB 连接测试通过")
    print("✅ 完整工作流测试通过")
    print()
    print("🚀 现在可以运行 'uv run generate' 命令了")

if __name__ == "__main__":
    main()
