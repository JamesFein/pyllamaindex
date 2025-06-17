#!/usr/bin/env python3
"""
修复 ChromaDB 数据库状态的脚本
"""
import os
import shutil
import sqlite3
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_chroma_db(chroma_db_path):
    """备份 ChromaDB 目录"""
    if not os.path.exists(chroma_db_path):
        logger.info("ChromaDB 目录不存在，无需备份")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{chroma_db_path}_backup_{timestamp}"
    
    try:
        shutil.copytree(chroma_db_path, backup_path)
        logger.info(f"✅ 已备份 ChromaDB 到: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"❌ 备份失败: {e}")
        return None

def completely_remove_chromadb(chroma_db_path):
    """完全删除 ChromaDB 目录"""
    if not os.path.exists(chroma_db_path):
        logger.info("ChromaDB 目录不存在")
        return True
    
    try:
        shutil.rmtree(chroma_db_path)
        logger.info(f"✅ 已完全删除 ChromaDB 目录: {chroma_db_path}")
        return True
    except Exception as e:
        logger.error(f"❌ 删除 ChromaDB 目录失败: {e}")
        return False

def create_fresh_chromadb(chroma_db_path):
    """创建全新的 ChromaDB"""
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        logger.info("🔧 创建全新的 ChromaDB...")
        
        # 确保目录存在
        os.makedirs(chroma_db_path, exist_ok=True)
        
        # 创建新的 ChromaDB 客户端
        chroma_client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        logger.info("✅ ChromaDB 客户端创建成功")
        
        # 创建默认集合
        collection_name = "document_vectors"
        collection = chroma_client.create_collection(collection_name)
        logger.info(f"✅ 创建集合: {collection_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建 ChromaDB 失败: {e}")
        return False

def verify_chromadb(chroma_db_path):
    """验证 ChromaDB 是否正常工作"""
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        logger.info("🔍 验证 ChromaDB...")
        
        # 连接到 ChromaDB
        chroma_client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 检查集合
        collection_name = "document_vectors"
        collection = chroma_client.get_collection(collection_name)
        count = collection.count()
        
        logger.info(f"✅ ChromaDB 验证成功，集合 {collection_name} 包含 {count} 个向量")
        return True
        
    except Exception as e:
        logger.error(f"❌ ChromaDB 验证失败: {e}")
        return False

def test_storage_context():
    """测试存储上下文创建"""
    try:
        from app.storage_config import get_storage_context
        
        logger.info("🔧 测试存储上下文创建...")
        storage_context = get_storage_context("storage")
        logger.info("✅ 存储上下文创建成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 存储上下文创建失败: {e}")
        return False

def main():
    """主修复流程"""
    storage_dir = "storage"
    chroma_db_path = os.path.join(storage_dir, "chroma_db")
    
    print("🔧 开始修复 ChromaDB")
    print("=" * 50)
    
    # 1. 备份现有的 ChromaDB
    backup_path = backup_chroma_db(chroma_db_path)
    
    # 2. 完全删除现有的 ChromaDB
    if not completely_remove_chromadb(chroma_db_path):
        print("❌ 修复失败：无法删除现有 ChromaDB")
        return
    
    # 3. 创建全新的 ChromaDB
    if not create_fresh_chromadb(chroma_db_path):
        print("❌ 修复失败：无法创建新的 ChromaDB")
        return
    
    # 4. 验证 ChromaDB
    if not verify_chromadb(chroma_db_path):
        print("❌ 修复失败：ChromaDB 验证失败")
        return
    
    # 5. 测试存储上下文
    if not test_storage_context():
        print("❌ 修复失败：存储上下文测试失败")
        return
    
    print()
    print("🎉 ChromaDB 修复完成！")
    print("=" * 50)
    print("✅ 已创建全新的 ChromaDB")
    print("✅ 存储上下文测试通过")
    if backup_path:
        print(f"📁 备份保存在: {backup_path}")
    print()
    print("🚀 现在可以运行 generate 命令了")

if __name__ == "__main__":
    main()
