#!/usr/bin/env python3
"""
清理存储目录中的数据库文件
"""
import os
import shutil
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_storage_files():
    """分析存储目录中的文件"""
    storage_dir = "storage"
    
    print("📁 存储目录文件分析")
    print("=" * 60)
    
    if not os.path.exists(storage_dir):
        print("❌ 存储目录不存在")
        return
    
    # 当前正在使用的文件（根据 storage_config.py）
    current_files = {
        "chroma_db_new/": "✅ 当前使用的 ChromaDB 向量数据库",
        "docstore.db": "✅ 当前使用的 SQLite 文档存储",
        "index_store.db": "✅ 当前使用的 SQLite 索引存储"
    }
    
    # 可以删除的文件
    deletable_files = {
        "chroma_db/": "❌ 旧的 ChromaDB 数据库（已损坏）",
        "chroma_db_backup_*/": "❌ ChromaDB 备份文件（调试时创建）",
        "graph_store.json": "❌ 图存储（项目不使用图功能）",
        "image__vector_store.json": "❌ 图像向量存储（项目只处理文本）"
    }
    
    print("🔍 文件分析结果:")
    print()
    
    # 分析实际存在的文件
    for item in os.listdir(storage_dir):
        item_path = os.path.join(storage_dir, item)
        size = get_size_info(item_path)
        
        if item in ["chroma_db_new", "docstore.db", "index_store.db"]:
            print(f"✅ {item:<25} | {size:<15} | 当前使用中")
        elif item == "chroma_db":
            print(f"❌ {item:<25} | {size:<15} | 旧的损坏数据库")
        elif item.startswith("chroma_db_backup_"):
            print(f"❌ {item:<25} | {size:<15} | 调试备份文件")
        elif item == "graph_store.json":
            print(f"❌ {item:<25} | {size:<15} | 图存储（未使用）")
        elif item == "image__vector_store.json":
            print(f"❌ {item:<25} | {size:<15} | 图像存储（未使用）")
        else:
            print(f"❓ {item:<25} | {size:<15} | 未知文件")
    
    return True

def get_size_info(path):
    """获取文件或目录大小信息"""
    try:
        if os.path.isfile(path):
            size = os.path.getsize(path)
            return format_size(size)
        elif os.path.isdir(path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except:
                        pass
            return format_size(total_size)
        else:
            return "未知"
    except:
        return "错误"

def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def cleanup_storage():
    """清理存储目录"""
    storage_dir = "storage"
    
    print("\n🧹 开始清理存储目录")
    print("=" * 60)
    
    # 要删除的文件和目录
    items_to_delete = []
    
    for item in os.listdir(storage_dir):
        item_path = os.path.join(storage_dir, item)
        
        # 检查是否应该删除
        should_delete = False
        reason = ""
        
        if item == "chroma_db":
            should_delete = True
            reason = "旧的损坏 ChromaDB 数据库"
        elif item.startswith("chroma_db_backup_"):
            should_delete = True
            reason = "调试时创建的备份文件"
        elif item == "graph_store.json":
            should_delete = True
            reason = "图存储文件（项目不使用图功能）"
        elif item == "image__vector_store.json":
            should_delete = True
            reason = "图像向量存储（项目只处理文本）"
        
        if should_delete:
            items_to_delete.append((item_path, reason))
    
    if not items_to_delete:
        print("✅ 没有需要清理的文件")
        return
    
    print("📋 将要删除的文件:")
    total_size = 0
    for item_path, reason in items_to_delete:
        size_info = get_size_info(item_path)
        print(f"  - {os.path.basename(item_path):<25} | {size_info:<15} | {reason}")
        
        # 计算总大小
        try:
            if os.path.isfile(item_path):
                total_size += os.path.getsize(item_path)
            elif os.path.isdir(item_path):
                for dirpath, dirnames, filenames in os.walk(item_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(filepath)
                        except:
                            pass
        except:
            pass
    
    print(f"\n💾 总共可释放空间: {format_size(total_size)}")
    
    # 执行删除
    print("\n🗑️  开始删除...")
    deleted_count = 0
    
    for item_path, reason in items_to_delete:
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                logger.info(f"删除文件: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                logger.info(f"删除目录: {item_path}")
            deleted_count += 1
        except Exception as e:
            logger.error(f"删除失败 {item_path}: {e}")
    
    print(f"✅ 成功删除 {deleted_count} 个项目")
    print(f"💾 释放空间: {format_size(total_size)}")

def verify_current_setup():
    """验证当前设置是否正常"""
    print("\n🔍 验证当前存储设置")
    print("=" * 60)
    
    storage_dir = "storage"
    required_files = {
        "chroma_db_new": "ChromaDB 向量数据库目录",
        "docstore.db": "SQLite 文档存储",
        "index_store.db": "SQLite 索引存储"
    }
    
    all_good = True
    
    for file_name, description in required_files.items():
        file_path = os.path.join(storage_dir, file_name)
        if os.path.exists(file_path):
            size_info = get_size_info(file_path)
            print(f"✅ {file_name:<20} | {size_info:<15} | {description}")
        else:
            print(f"❌ {file_name:<20} | 不存在        | {description}")
            all_good = False
    
    if all_good:
        print("\n🎉 当前存储设置完整，系统可以正常运行！")
    else:
        print("\n⚠️  存储设置不完整，可能需要重新生成索引")
    
    return all_good

def main():
    """主清理流程"""
    print("🧹 存储目录清理工具")
    print("=" * 60)
    
    # 1. 分析文件
    analyze_storage_files()
    
    # 2. 清理文件
    cleanup_storage()
    
    # 3. 验证设置
    verify_current_setup()
    
    print("\n" + "=" * 60)
    print("🎯 清理完成！")
    print("📁 保留的文件:")
    print("  - chroma_db_new/     : 当前使用的 ChromaDB 向量数据库")
    print("  - docstore.db        : 当前使用的 SQLite 文档存储")
    print("  - index_store.db     : 当前使用的 SQLite 索引存储")
    print("\n💡 这些是系统正常运行所需的最小文件集合")

if __name__ == "__main__":
    main()
