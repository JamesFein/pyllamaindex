#!/usr/bin/env python3
"""
检查数据库中的重复数据和数据库状态
"""
import sqlite3
import json
from collections import Counter
import os

def check_database_status():
    """检查数据库状态和重复数据"""
    db_path = "storage/docstore.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"📊 检查数据库: {db_path}")
    print("=" * 50)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. 检查表结构
        print("📋 数据库表结构:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        print()
        
        # 2. 检查documents表
        if any('documents' in table for table in tables):
            print("📄 Documents表统计:")
            cursor.execute("SELECT COUNT(*) FROM documents")
            total_docs = cursor.fetchone()[0]
            print(f"  总文档数: {total_docs}")
            
            # 检查重复的doc_id
            cursor.execute("""
                SELECT doc_id, COUNT(*) as count 
                FROM documents 
                GROUP BY doc_id 
                HAVING COUNT(*) > 1
                ORDER BY count DESC
            """)
            duplicates = cursor.fetchall()
            if duplicates:
                print(f"  ⚠️  发现 {len(duplicates)} 个重复的doc_id:")
                for doc_id, count in duplicates[:10]:  # 只显示前10个
                    print(f"    - {doc_id}: {count} 次")
                if len(duplicates) > 10:
                    print(f"    ... 还有 {len(duplicates) - 10} 个重复项")
            else:
                print("  ✅ 没有发现重复的doc_id")
            
            # 检查文件名分布
            cursor.execute("""
                SELECT file_name, COUNT(*) as count 
                FROM documents 
                WHERE file_name IS NOT NULL
                GROUP BY file_name 
                ORDER BY count DESC
                LIMIT 10
            """)
            file_counts = cursor.fetchall()
            if file_counts:
                print(f"  📁 文件名分布 (前10个):")
                for file_name, count in file_counts:
                    print(f"    - {file_name}: {count} 个文档块")
            print()
        
        # 3. 检查files表
        if any('files' in table for table in tables):
            print("📁 Files表统计:")
            cursor.execute("SELECT COUNT(*) FROM files")
            total_files = cursor.fetchone()[0]
            print(f"  总文件数: {total_files}")
            
            # 检查重复的file_name
            cursor.execute("""
                SELECT file_name, COUNT(*) as count 
                FROM files 
                GROUP BY file_name 
                HAVING COUNT(*) > 1
                ORDER BY count DESC
            """)
            file_duplicates = cursor.fetchall()
            if file_duplicates:
                print(f"  ⚠️  发现 {len(file_duplicates)} 个重复的文件名:")
                for file_name, count in file_duplicates:
                    print(f"    - {file_name}: {count} 次")
            else:
                print("  ✅ 没有发现重复的文件名")
            
            # 显示最近上传的文件
            cursor.execute("""
                SELECT file_name, upload_date, file_size 
                FROM files 
                ORDER BY upload_date DESC 
                LIMIT 5
            """)
            recent_files = cursor.fetchall()
            if recent_files:
                print(f"  📅 最近上传的文件:")
                for file_name, upload_date, file_size in recent_files:
                    print(f"    - {file_name} ({file_size} bytes) - {upload_date}")
            print()
        
        # 4. 检查ref_doc_info表
        if any('ref_doc_info' in table for table in tables):
            print("🔗 Ref_doc_info表统计:")
            cursor.execute("SELECT COUNT(*) FROM ref_doc_info")
            total_refs = cursor.fetchone()[0]
            print(f"  总引用文档数: {total_refs}")
            print()

def suggest_cleanup_actions():
    """建议清理操作"""
    print("🛠️  数据库清理建议:")
    print("=" * 50)
    print("1. 🔄 完全重置数据库 (推荐)")
    print("   - 删除现有数据库文件")
    print("   - 重新初始化干净的数据库")
    print("   - 重新索引所有文档")
    print()
    print("2. 🧹 清理重复数据")
    print("   - 保留最新的记录")
    print("   - 删除重复的文档块")
    print("   - 重建索引")
    print()
    print("3. 🔍 检查数据一致性")
    print("   - 验证文件系统与数据库的一致性")
    print("   - 清理孤立的记录")
    print()

if __name__ == "__main__":
    check_database_status()
    suggest_cleanup_actions()
