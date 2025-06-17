#!/usr/bin/env python3
"""
检查数据库中的重复数据
"""
import sqlite3
import chromadb
from chromadb.config import Settings as ChromaSettings

def check_sqlite_data():
    """检查 SQLite 数据库中的数据"""
    print("🔍 检查 SQLite 数据库...")
    
    # 检查 documents 表
    with sqlite3.connect('storage/docstore.db') as conn:
        cursor = conn.execute('SELECT COUNT(*) FROM documents')
        doc_count = cursor.fetchone()[0]
        print(f'📊 Documents 表中有 {doc_count} 条记录')
        
        # 按文件分组统计
        cursor = conn.execute('''
            SELECT file_name, COUNT(*) as chunk_count 
            FROM documents 
            GROUP BY file_name 
            ORDER BY file_name
        ''')
        print("📄 按文件分组的文档块数量:")
        for row in cursor.fetchall():
            print(f'  - {row[0]}: {row[1]} 个块')
        
        # 检查是否有重复的 doc_id
        cursor = conn.execute('''
            SELECT doc_id, COUNT(*) as count 
            FROM documents 
            GROUP BY doc_id 
            HAVING COUNT(*) > 1
        ''')
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"⚠️  发现 {len(duplicates)} 个重复的 doc_id:")
            for row in duplicates:
                print(f'  - {row[0]}: {row[1]} 次')
        else:
            print("✅ 没有重复的 doc_id")

    # 检查 files 表
    with sqlite3.connect('storage/docstore.db') as conn:
        cursor = conn.execute('SELECT COUNT(*) FROM files')
        file_count = cursor.fetchone()[0]
        print(f'\n📊 Files 表中有 {file_count} 条记录')
        
        cursor = conn.execute('SELECT file_id, file_name, created_at, updated_at FROM files')
        print("📁 文件记录:")
        for row in cursor.fetchall():
            print(f'  - {row[0]} | {row[1]} | 创建: {row[2]} | 更新: {row[3]}')

def check_chromadb_data():
    """检查 ChromaDB 中的向量数据"""
    print("\n🔍 检查 ChromaDB 向量数据...")
    
    try:
        chroma_client = chromadb.PersistentClient(
            path='storage/chroma_db_new',
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        collection = chroma_client.get_collection('document_vectors')
        count = collection.count()
        print(f'📊 ChromaDB 中有 {count} 个向量')
        
        # 获取所有向量的 ID
        result = collection.get()
        if result['ids']:
            print(f'🔢 向量 IDs: {len(result["ids"])} 个')
            
            # 检查是否有重复的 ID
            unique_ids = set(result['ids'])
            if len(unique_ids) != len(result['ids']):
                print(f"⚠️  发现重复的向量 ID: {len(result['ids']) - len(unique_ids)} 个重复")
            else:
                print("✅ 没有重复的向量 ID")
            
            # 显示前几个 ID
            print("🔤 前10个向量 ID:")
            for i, id in enumerate(result['ids'][:10]):
                print(f'  - {id}')
            if len(result['ids']) > 10:
                print(f'  ... 还有 {len(result["ids"]) - 10} 个')
        
    except Exception as e:
        print(f"❌ 检查 ChromaDB 失败: {e}")

def analyze_duplication_issue():
    """分析重复数据问题"""
    print("\n🔍 分析重复数据问题...")
    
    # 检查 generate.py 的逻辑
    print("📋 Generate 命令的行为:")
    print("1. 每次运行都会重新读取 data 目录中的所有文件")
    print("2. 为每个文档生成新的 node_id (UUID)")
    print("3. 使用 INSERT OR REPLACE 更新 SQLite 数据")
    print("4. 向 ChromaDB 添加新的向量（可能重复）")
    
    # 检查当前的重复情况
    with sqlite3.connect('storage/docstore.db') as conn:
        cursor = conn.execute('''
            SELECT file_name, COUNT(DISTINCT doc_id) as unique_docs, COUNT(*) as total_docs
            FROM documents 
            GROUP BY file_name
        ''')
        
        print("\n📊 重复情况分析:")
        total_unique = 0
        total_all = 0
        for row in cursor.fetchall():
            file_name, unique_docs, total_docs = row
            total_unique += unique_docs
            total_all += total_docs
            if total_docs > unique_docs:
                print(f"⚠️  {file_name}: {unique_docs} 个唯一文档, {total_docs} 个总文档 (有重复)")
            else:
                print(f"✅ {file_name}: {unique_docs} 个文档 (无重复)")
        
        print(f"\n📈 总计: {total_unique} 个唯一文档, {total_all} 个总文档")
        if total_all > total_unique:
            print(f"⚠️  总共有 {total_all - total_unique} 个重复文档")

def main():
    """主检查流程"""
    print("🔍 开始检查数据库重复数据")
    print("=" * 60)
    
    check_sqlite_data()
    check_chromadb_data()
    analyze_duplication_issue()
    
    print("\n" + "=" * 60)
    print("🎯 结论:")
    print("重复运行 'uv run generate' 会导致:")
    print("1. ✅ SQLite files 表: 不会重复 (使用 INSERT OR REPLACE)")
    print("2. ❌ SQLite documents 表: 会产生重复记录 (新的 node_id)")
    print("3. ❌ ChromaDB 向量: 会产生重复向量 (新的嵌入)")
    print("\n💡 建议: 重复运行前先重置数据库，或改进去重逻辑")

if __name__ == "__main__":
    main()
