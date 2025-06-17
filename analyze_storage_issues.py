#!/usr/bin/env python3
"""
分析当前存储逻辑的问题
"""
import sqlite3
import json
import os
import chromadb
from chromadb.config import Settings as ChromaSettings

def analyze_docstore():
    """分析 docstore.db 的问题"""
    print("🔍 分析 DOCSTORE.DB")
    print("=" * 60)
    
    if not os.path.exists('storage/docstore.db'):
        print("❌ docstore.db 不存在")
        return
    
    conn = sqlite3.connect('storage/docstore.db')
    
    # 1. 检查 documents 表结构
    print("📋 Documents 表结构:")
    cursor = conn.execute("PRAGMA table_info(documents)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 2. 检查 documents 表数据
    print(f"\n📊 Documents 表数据分析:")
    cursor = conn.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]
    print(f"  总记录数: {total_docs}")
    
    if total_docs > 0:
        # 检查 chunk_index 分布
        cursor = conn.execute("SELECT chunk_index, COUNT(*) FROM documents GROUP BY chunk_index ORDER BY chunk_index")
        chunk_distribution = cursor.fetchall()
        print(f"  Chunk_index 分布:")
        for chunk_idx, count in chunk_distribution:
            print(f"    chunk_index={chunk_idx}: {count} 条记录")
        
        # 检查文件名重复情况
        cursor = conn.execute("SELECT file_name, COUNT(*) FROM documents WHERE file_name IS NOT NULL GROUP BY file_name")
        file_duplicates = cursor.fetchall()
        print(f"  文件名重复情况:")
        for file_name, count in file_duplicates:
            if count > 1:
                print(f"    ⚠️  {file_name}: {count} 条记录 (重复)")
            else:
                print(f"    ✅ {file_name}: {count} 条记录")
    
    # 3. 检查 files 表
    print(f"\n📁 Files 表数据分析:")
    cursor = conn.execute("SELECT COUNT(*) FROM files")
    total_files = cursor.fetchone()[0]
    print(f"  总记录数: {total_files}")
    
    if total_files > 0:
        cursor = conn.execute("SELECT file_id, file_name FROM files")
        files = cursor.fetchall()
        for file_id, file_name in files:
            print(f"    {file_id}: {file_name}")
    
    conn.close()

def analyze_chroma():
    """分析 ChromaDB 的问题"""
    print("\n🧠 分析 CHROMADB")
    print("=" * 60)
    
    chroma_path = 'storage/chroma_db_new'
    if not os.path.exists(chroma_path):
        print("❌ ChromaDB 不存在")
        return
    
    try:
        client = chromadb.PersistentClient(
            path=chroma_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 获取集合
        collection = client.get_collection('document_vectors')
        count = collection.count()
        print(f"📊 向量总数: {count}")
        
        if count > 0:
            # 获取所有数据
            result = collection.get()
            print(f"🔢 实际获取到的向量数: {len(result['ids'])}")
            
            # 检查 ID 重复
            unique_ids = set(result['ids'])
            if len(unique_ids) != len(result['ids']):
                print(f"⚠️  发现重复的向量 ID: {len(result['ids']) - len(unique_ids)} 个重复")
            else:
                print("✅ 没有重复的向量 ID")
            
            # 分析元数据
            if result['metadatas']:
                print(f"📋 元数据分析 (前5个):")
                for i, metadata in enumerate(result['metadatas'][:5]):
                    if metadata:
                        file_name = metadata.get('file_name', 'Unknown')
                        chunk_index = metadata.get('chunk_index', 'Unknown')
                        print(f"  {i+1}. file_name: {file_name}, chunk_index: {chunk_index}")
                    else:
                        print(f"  {i+1}. 空元数据")
        
    except Exception as e:
        print(f"❌ ChromaDB 分析失败: {e}")

def analyze_id_consistency():
    """分析 docstore 和 chroma 之间的 ID 一致性"""
    print("\n🔗 分析 ID 一致性")
    print("=" * 60)
    
    # 获取 docstore 中的所有 doc_id
    docstore_ids = set()
    if os.path.exists('storage/docstore.db'):
        conn = sqlite3.connect('storage/docstore.db')
        cursor = conn.execute("SELECT doc_id FROM documents")
        docstore_ids = {row[0] for row in cursor.fetchall()}
        conn.close()
        print(f"📄 Docstore 中的 doc_id 数量: {len(docstore_ids)}")
    
    # 获取 chroma 中的所有 ID
    chroma_ids = set()
    chroma_path = 'storage/chroma_db_new'
    if os.path.exists(chroma_path):
        try:
            client = chromadb.PersistentClient(
                path=chroma_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            collection = client.get_collection('document_vectors')
            result = collection.get()
            chroma_ids = set(result['ids'])
            print(f"🧠 ChromaDB 中的 ID 数量: {len(chroma_ids)}")
        except Exception as e:
            print(f"❌ 无法获取 ChromaDB IDs: {e}")
    
    # 比较一致性
    if docstore_ids and chroma_ids:
        common_ids = docstore_ids & chroma_ids
        docstore_only = docstore_ids - chroma_ids
        chroma_only = chroma_ids - docstore_ids
        
        print(f"🔗 共同 ID 数量: {len(common_ids)}")
        print(f"📄 仅在 Docstore 中的 ID: {len(docstore_only)}")
        print(f"🧠 仅在 ChromaDB 中的 ID: {len(chroma_only)}")
        
        if docstore_only:
            print(f"  Docstore 独有 ID (前5个): {list(docstore_only)[:5]}")
        if chroma_only:
            print(f"  ChromaDB 独有 ID (前5个): {list(chroma_only)[:5]}")

def main():
    """主函数"""
    print("🔍 存储逻辑问题分析")
    print("=" * 80)
    
    analyze_docstore()
    analyze_chroma()
    analyze_id_consistency()
    
    print("\n💡 问题总结:")
    print("1. 检查 documents 表是否真的用于存储文本块信息")
    print("2. 检查 chunk_index 是否正确设置")
    print("3. 检查同名文件是否正确处理")
    print("4. 检查 docstore 和 chroma 之间的 ID 一致性")

if __name__ == "__main__":
    main()
