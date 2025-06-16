#!/usr/bin/env python3
"""
数据库重置脚本 - 安全地重置所有存储组件
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

def backup_storage(storage_dir="storage"):
    """备份当前存储目录"""
    if not os.path.exists(storage_dir):
        logger.info(f"存储目录 {storage_dir} 不存在，无需备份")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"{storage_dir}_backup_{timestamp}"
    
    try:
        shutil.copytree(storage_dir, backup_dir)
        logger.info(f"✅ 已备份存储目录到: {backup_dir}")
        return backup_dir
    except Exception as e:
        logger.error(f"❌ 备份失败: {e}")
        return None

def analyze_current_storage(storage_dir="storage"):
    """分析当前存储状态"""
    logger.info("📊 分析当前存储状态...")
    
    if not os.path.exists(storage_dir):
        logger.info("存储目录不存在")
        return
    
    # 统计文件大小
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(storage_dir):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            total_size += size
            file_count += 1
            logger.info(f"  - {os.path.relpath(file_path, storage_dir)}: {size:,} bytes")
    
    logger.info(f"📁 总计: {file_count} 个文件, {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    
    # 检查数据库内容
    db_files = ["docstore.db", "index_store.db", "chroma_db/chroma.sqlite3"]
    for db_file in db_files:
        db_path = os.path.join(storage_dir, db_file)
        if os.path.exists(db_path):
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    
                    logger.info(f"🗄️  {db_file}:")
                    for table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                        count = cursor.fetchone()[0]
                        logger.info(f"    - {table[0]}: {count:,} 行")
            except Exception as e:
                logger.warning(f"⚠️  无法读取 {db_file}: {e}")

def remove_storage_directory(storage_dir="storage"):
    """删除存储目录"""
    if not os.path.exists(storage_dir):
        logger.info(f"存储目录 {storage_dir} 不存在")
        return True
    
    try:
        shutil.rmtree(storage_dir)
        logger.info(f"🗑️  已删除存储目录: {storage_dir}")
        return True
    except Exception as e:
        logger.error(f"❌ 删除存储目录失败: {e}")
        return False

def create_clean_storage(storage_dir="storage"):
    """创建干净的存储目录结构"""
    try:
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"📁 已创建干净的存储目录: {storage_dir}")
        return True
    except Exception as e:
        logger.error(f"❌ 创建存储目录失败: {e}")
        return False

def initialize_clean_databases(storage_dir="storage"):
    """初始化干净的数据库"""
    try:
        from app.storage_config import get_storage_context
        
        logger.info("🔧 初始化干净的存储上下文...")
        storage_context = get_storage_context(storage_dir)
        
        # 验证数据库是否正确创建
        docstore_path = os.path.join(storage_dir, "docstore.db")
        index_store_path = os.path.join(storage_dir, "index_store.db")
        chroma_path = os.path.join(storage_dir, "chroma_db")
        
        if os.path.exists(docstore_path):
            logger.info(f"✅ docstore.db 已创建: {os.path.getsize(docstore_path)} bytes")
        
        if os.path.exists(index_store_path):
            logger.info(f"✅ index_store.db 已创建: {os.path.getsize(index_store_path)} bytes")
        
        if os.path.exists(chroma_path):
            logger.info(f"✅ chroma_db 已创建")
        
        logger.info("🎉 存储上下文初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 初始化存储上下文失败: {e}")
        return False

def verify_reset(storage_dir="storage"):
    """验证重置结果"""
    logger.info("🔍 验证重置结果...")
    
    if not os.path.exists(storage_dir):
        logger.error("❌ 存储目录不存在")
        return False
    
    # 检查必需的文件
    required_files = [
        "docstore.db",
        "index_store.db",
        "chroma_db"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(storage_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ 缺少必需文件: {missing_files}")
        return False
    
    # 检查不应该存在的文件
    unwanted_files = [
        "graph_store.json",
        "image__vector_store.json"
    ]
    
    found_unwanted = []
    for file in unwanted_files:
        file_path = os.path.join(storage_dir, file)
        if os.path.exists(file_path):
            found_unwanted.append(file)
    
    if found_unwanted:
        logger.warning(f"⚠️  发现不需要的文件: {found_unwanted}")
    
    logger.info("✅ 数据库重置验证完成")
    return True

def main():
    """主重置流程"""
    storage_dir = "storage"
    
    print("🔄 开始数据库重置流程")
    print("=" * 50)
    
    # 1. 分析当前状态
    analyze_current_storage(storage_dir)
    print()
    
    # 2. 确认重置
    response = input("⚠️  确定要重置数据库吗？这将删除所有现有数据！(y/N): ")
    if response.lower() != 'y':
        print("❌ 重置已取消")
        return
    
    # 3. 备份
    backup_dir = backup_storage(storage_dir)
    if not backup_dir:
        response = input("⚠️  备份失败，是否继续？(y/N): ")
        if response.lower() != 'y':
            print("❌ 重置已取消")
            return
    
    # 4. 删除现有存储
    if not remove_storage_directory(storage_dir):
        print("❌ 重置失败：无法删除现有存储")
        return
    
    # 5. 创建干净的存储
    if not create_clean_storage(storage_dir):
        print("❌ 重置失败：无法创建存储目录")
        return
    
    # 6. 初始化数据库
    if not initialize_clean_databases(storage_dir):
        print("❌ 重置失败：无法初始化数据库")
        return
    
    # 7. 验证结果
    if not verify_reset(storage_dir):
        print("❌ 重置验证失败")
        return
    
    print()
    print("🎉 数据库重置完成！")
    print("=" * 50)
    print("✅ 已删除所有旧数据")
    print("✅ 已创建干净的数据库结构")
    print("✅ 已移除冗余文件 (graph_store.json, image__vector_store.json)")
    if backup_dir:
        print(f"📁 备份保存在: {backup_dir}")
    print()
    print("🚀 现在可以重新上传文档并重建索引")

if __name__ == "__main__":
    main()
