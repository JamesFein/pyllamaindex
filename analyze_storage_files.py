#!/usr/bin/env python3
"""
分析存储目录中的所有数据库文件
"""
import sqlite3
import json
import os
from pathlib import Path

def analyze_storage_directory():
    """分析存储目录中的所有文件"""
    storage_dir = Path("storage")
    
    print("📁 存储目录分析报告")
    print("=" * 60)
    
    # 1. 分析所有文件
    print("📋 文件清单:")
    for file_path in storage_dir.rglob("*"):
        if file_path.is_file():
            size = file_path.stat().st_size
            print(f"  - {file_path.relative_to(storage_dir)}: {size:,} bytes")
    print()
    
    # 2. 分析SQLite数据库
    sqlite_files = [
        "docstore.db",
        "index_store.db", 
        "chroma_db/chroma.sqlite3"
    ]
    
    for db_file in sqlite_files:
        db_path = storage_dir / db_file
        if db_path.exists():
            print(f"🗄️  分析 {db_file}:")
            analyze_sqlite_db(db_path)
            print()
    
    # 3. 分析JSON文件
    json_files = [
        "graph_store.json",
        "image__vector_store.json"
    ]
    
    for json_file in json_files:
        json_path = storage_dir / json_file
        if json_path.exists():
            print(f"📄 分析 {json_file}:")
            analyze_json_file(json_path)
            print()

def analyze_sqlite_db(db_path):
    """分析SQLite数据库"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 获取表列表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"    表数量: {len(tables)}")
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                print(f"    - {table}: {count:,} 行, {len(columns)} 列")
                
                # 显示列信息
                for col in columns[:5]:  # 只显示前5列
                    print(f"      * {col[1]} ({col[2]})")
                if len(columns) > 5:
                    print(f"      ... 还有 {len(columns) - 5} 列")
                
                # 如果有数据，显示一些样本
                if count > 0 and count < 1000:  # 只对小表显示样本
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    samples = cursor.fetchall()
                    if samples:
                        print(f"      样本数据: {len(samples)} 行")
                        for i, sample in enumerate(samples):
                            # 只显示前3个字段，避免输出过长
                            sample_str = str(sample[:3])
                            if len(sample_str) > 100:
                                sample_str = sample_str[:100] + "..."
                            print(f"        [{i+1}] {sample_str}")
                
    except Exception as e:
        print(f"    ❌ 错误: {e}")

def analyze_json_file(json_path):
    """分析JSON文件"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"    文件大小: {json_path.stat().st_size:,} bytes")
        print(f"    JSON结构:")
        
        def analyze_json_structure(obj, indent=6):
            if isinstance(obj, dict):
                print(f"{' ' * indent}字典 - {len(obj)} 个键:")
                for key, value in list(obj.items())[:5]:  # 只显示前5个键
                    print(f"{' ' * (indent+2)}- {key}: {type(value).__name__}")
                    if isinstance(value, (dict, list)) and len(str(value)) < 200:
                        analyze_json_structure(value, indent + 4)
                if len(obj) > 5:
                    print(f"{' ' * (indent+2)}... 还有 {len(obj) - 5} 个键")
            elif isinstance(obj, list):
                print(f"{' ' * indent}列表 - {len(obj)} 个元素")
                if obj and len(obj) <= 3:
                    for i, item in enumerate(obj):
                        print(f"{' ' * (indent+2)}[{i}]: {type(item).__name__}")
            else:
                value_str = str(obj)
                if len(value_str) > 50:
                    value_str = value_str[:50] + "..."
                print(f"{' ' * indent}值: {value_str}")
        
        analyze_json_structure(data)
        
    except Exception as e:
        print(f"    ❌ 错误: {e}")

def check_file_usage():
    """检查文件的实际使用情况"""
    print("🔍 文件使用情况分析:")
    print("=" * 60)
    
    # 检查代码中对这些文件的引用
    storage_files = [
        "docstore.db",
        "index_store.db", 
        "chroma.sqlite3",
        "graph_store.json",
        "image__vector_store.json"
    ]
    
    for file_name in storage_files:
        print(f"📄 {file_name}:")
        # 这里可以添加代码来搜索文件引用
        # 但由于我们在分析脚本中，先手动分析
        if "graph_store" in file_name:
            print("    - 用途: 图存储（知识图谱）")
            print("    - 项目需要: ❌ 仅处理txt文件，不需要图结构")
        elif "image" in file_name:
            print("    - 用途: 图像向量存储")
            print("    - 项目需要: ❌ 仅处理txt文件，不处理图像")
        elif "chroma" in file_name:
            print("    - 用途: ChromaDB向量数据库")
            print("    - 项目需要: ✅ 用于文本向量存储和检索")
        elif "docstore" in file_name:
            print("    - 用途: 文档存储")
            print("    - 项目需要: ✅ 存储文档和文本块")
        elif "index_store" in file_name:
            print("    - 用途: 索引结构存储")
            print("    - 项目需要: ✅ 存储索引元数据")
        print()

if __name__ == "__main__":
    analyze_storage_directory()
    check_file_usage()
