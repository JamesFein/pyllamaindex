#!/usr/bin/env python3
"""
强制数据库重置脚本 - 处理文件被占用的情况
"""
import os
import shutil
import time
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def force_remove_file(file_path, max_attempts=5):
    """强制删除文件，处理被占用的情况"""
    for attempt in range(max_attempts):
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            logger.info(f"✅ 已删除: {file_path}")
            return True
        except PermissionError as e:
            logger.warning(f"⚠️  尝试 {attempt + 1}/{max_attempts}: 文件被占用 {file_path}")
            if attempt < max_attempts - 1:
                time.sleep(2)  # 等待2秒后重试
            else:
                logger.error(f"❌ 无法删除文件 {file_path}: {e}")
                return False
        except Exception as e:
            logger.error(f"❌ 删除文件失败 {file_path}: {e}")
            return False
    return False

def force_reset_storage(storage_dir="storage"):
    """强制重置存储目录"""
    logger.info("🔄 开始强制重置存储...")
    
    if not os.path.exists(storage_dir):
        logger.info(f"存储目录 {storage_dir} 不存在")
        return True
    
    # 逐个删除文件
    files_to_remove = []
    for root, dirs, files in os.walk(storage_dir):
        for file in files:
            files_to_remove.append(os.path.join(root, file))
    
    # 先删除所有文件
    failed_files = []
    for file_path in files_to_remove:
        if not force_remove_file(file_path):
            failed_files.append(file_path)
    
    if failed_files:
        logger.error(f"❌ 以下文件无法删除: {failed_files}")
        return False
    
    # 删除空目录
    try:
        for root, dirs, files in os.walk(storage_dir, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    os.rmdir(dir_path)
                    logger.info(f"✅ 已删除目录: {dir_path}")
                except OSError:
                    pass  # 目录可能不为空，忽略
        
        # 最后删除根目录
        os.rmdir(storage_dir)
        logger.info(f"✅ 已删除存储根目录: {storage_dir}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 删除目录失败: {e}")
        return False

def create_clean_storage_context():
    """创建干净的存储上下文"""
    try:
        from app.storage_config import get_storage_context
        
        logger.info("🔧 创建干净的存储上下文...")
        storage_context = get_storage_context("storage")
        
        # 验证创建结果
        storage_files = [
            "storage/docstore.db",
            "storage/index_store.db",
            "storage/chroma_db"
        ]
        
        all_created = True
        for file_path in storage_files:
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    logger.info(f"✅ {file_path}: {size} bytes")
                else:
                    logger.info(f"✅ {file_path}: 目录已创建")
            else:
                logger.error(f"❌ {file_path}: 未创建")
                all_created = False
        
        return all_created
        
    except Exception as e:
        logger.error(f"❌ 创建存储上下文失败: {e}")
        return False

def verify_clean_state():
    """验证清理状态"""
    logger.info("🔍 验证清理状态...")
    
    # 检查不应该存在的文件
    unwanted_files = [
        "storage/graph_store.json",
        "storage/image__vector_store.json"
    ]
    
    clean = True
    for file_path in unwanted_files:
        if os.path.exists(file_path):
            logger.warning(f"⚠️  发现不需要的文件: {file_path}")
            clean = False
    
    if clean:
        logger.info("✅ 存储状态干净")
    
    return clean

def main():
    """主重置流程"""
    print("🔄 强制数据库重置")
    print("=" * 40)
    
    # 1. 强制删除存储目录
    if not force_reset_storage("storage"):
        print("❌ 强制重置失败")
        return
    
    # 2. 创建干净的存储
    if not create_clean_storage_context():
        print("❌ 创建存储上下文失败")
        return
    
    # 3. 验证状态
    if not verify_clean_state():
        print("⚠️  存储状态不完全干净")
    
    print()
    print("🎉 强制数据库重置完成！")
    print("=" * 40)
    print("✅ 已删除所有旧数据")
    print("✅ 已创建干净的数据库结构")
    print("✅ 已移除冗余文件")
    print()
    print("🚀 现在可以重新上传文档")

if __name__ == "__main__":
    main()
