#!/usr/bin/env python3
"""
强制清理被占用的文件
"""
import os
import shutil
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def force_cleanup_old_chroma():
    """强制清理旧的 chroma_db 目录"""
    storage_dir = "storage"
    old_chroma_path = os.path.join(storage_dir, "chroma_db")
    
    if not os.path.exists(old_chroma_path):
        print("✅ 旧的 chroma_db 目录已经不存在")
        return True
    
    print("🔧 尝试强制清理旧的 chroma_db 目录...")
    
    # 方法1: 尝试重命名目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_name = f"chroma_db_old_{timestamp}"
    temp_path = os.path.join(storage_dir, temp_name)
    
    try:
        os.rename(old_chroma_path, temp_path)
        logger.info(f"✅ 成功重命名 {old_chroma_path} -> {temp_path}")
        
        # 尝试删除重命名后的目录
        try:
            shutil.rmtree(temp_path)
            logger.info(f"✅ 成功删除 {temp_path}")
            return True
        except Exception as e:
            logger.warning(f"⚠️  重命名成功但删除失败: {e}")
            logger.info(f"📁 旧文件已重命名为: {temp_name}")
            return True
            
    except Exception as e:
        logger.error(f"❌ 重命名失败: {e}")
        
        # 方法2: 尝试逐个删除文件
        try:
            logger.info("🔧 尝试逐个删除文件...")
            deleted_files = 0
            
            for root, dirs, files in os.walk(old_chroma_path, topdown=False):
                # 删除文件
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        deleted_files += 1
                    except Exception as fe:
                        logger.warning(f"无法删除文件 {file_path}: {fe}")
                
                # 删除空目录
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        os.rmdir(dir_path)
                    except Exception as de:
                        logger.warning(f"无法删除目录 {dir_path}: {de}")
            
            # 尝试删除根目录
            try:
                os.rmdir(old_chroma_path)
                logger.info(f"✅ 成功删除根目录 {old_chroma_path}")
                return True
            except Exception as e:
                logger.warning(f"⚠️  删除了 {deleted_files} 个文件，但根目录仍被占用: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 逐个删除也失败: {e}")
            return False

def check_final_state():
    """检查最终的存储状态"""
    print("\n🔍 检查最终存储状态")
    print("=" * 50)
    
    storage_dir = "storage"
    
    if not os.path.exists(storage_dir):
        print("❌ 存储目录不存在")
        return
    
    print("📁 当前存储目录内容:")
    for item in sorted(os.listdir(storage_dir)):
        item_path = os.path.join(storage_dir, item)
        
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            size_str = format_size(size)
            print(f"  📄 {item:<25} | {size_str}")
        elif os.path.isdir(item_path):
            # 计算目录大小
            total_size = 0
            try:
                for dirpath, dirnames, filenames in os.walk(item_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(filepath)
                        except:
                            pass
            except:
                pass
            size_str = format_size(total_size)
            print(f"  📁 {item:<25} | {size_str}")
    
    # 检查必需文件
    required_files = ["chroma_db_new", "docstore.db", "index_store.db"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(storage_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  缺少必需文件: {', '.join(missing_files)}")
    else:
        print(f"\n✅ 所有必需文件都存在")

def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def main():
    """主清理流程"""
    print("🧹 强制清理工具")
    print("=" * 50)
    
    # 强制清理旧的 ChromaDB
    success = force_cleanup_old_chroma()
    
    if success:
        print("✅ 清理完成")
    else:
        print("⚠️  部分清理完成，可能有文件仍被占用")
    
    # 检查最终状态
    check_final_state()
    
    print("\n" + "=" * 50)
    print("🎯 最终状态:")
    print("✅ 保留文件:")
    print("  - chroma_db_new/  : 当前使用的 ChromaDB")
    print("  - docstore.db     : SQLite 文档存储")
    print("  - index_store.db  : SQLite 索引存储")
    
    # 检查是否还有旧文件
    if os.path.exists("storage/chroma_db"):
        print("\n⚠️  注意:")
        print("  - chroma_db/      : 旧文件仍存在（可能被进程占用）")
        print("  - 建议重启系统后再次尝试删除")
    else:
        print("\n🎉 清理完全成功！")

if __name__ == "__main__":
    main()
