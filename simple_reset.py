#!/usr/bin/env python3
"""
简单数据库重置脚本 - 重新创建存储上下文
"""
import os
import shutil
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simple_reset():
    """简单重置数据库"""
    storage_dir = "storage"
    
    print("🔄 开始简单数据库重置")
    print("=" * 40)
    
    # 1. 尝试删除存储目录
    if os.path.exists(storage_dir):
        try:
            shutil.rmtree(storage_dir)
            logger.info(f"✅ 已删除存储目录: {storage_dir}")
        except Exception as e:
            logger.warning(f"⚠️  无法完全删除存储目录: {e}")
            # 继续执行，让存储上下文重新创建
    
    # 2. 创建新的存储上下文
    try:
        from app.storage_config import get_storage_context
        
        logger.info("🔧 创建新的存储上下文...")
        storage_context = get_storage_context(storage_dir)
        
        # 验证创建结果
        required_files = [
            os.path.join(storage_dir, "docstore.db"),
            os.path.join(storage_dir, "index_store.db"),
            os.path.join(storage_dir, "chroma_db")
        ]
        
        all_created = True
        for file_path in required_files:
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    logger.info(f"✅ {file_path}: {size} bytes")
                else:
                    logger.info(f"✅ {file_path}: 目录已创建")
            else:
                logger.error(f"❌ {file_path}: 未创建")
                all_created = False
        
        if all_created:
            print()
            print("🎉 数据库重置完成！")
            print("=" * 40)
            print("✅ 已创建干净的数据库结构")
            print("🚀 现在可以重新上传文档并重建索引")
            return True
        else:
            print("❌ 数据库重置失败：部分文件未创建")
            return False
            
    except Exception as e:
        logger.error(f"❌ 创建存储上下文失败: {e}")
        print("❌ 数据库重置失败")
        return False

if __name__ == "__main__":
    simple_reset()
