#!/usr/bin/env python3
"""
检查 ChromaDB embedding_metadata 表的结构和数据
"""

import sqlite3
import os

def check_embedding_metadata():
    chroma_db_path = 'storage/chroma_db_new/chroma.sqlite3'
    
    if not os.path.exists(chroma_db_path):
        print(f"❌ ChromaDB 文件不存在: {chroma_db_path}")
        return
    
    try:
        conn = sqlite3.connect(chroma_db_path)
        
        # 1. 查看所有表
        print("=== 数据库中的所有表 ===")
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"📋 {table[0]}")
        
        # 2. 查看 embedding_metadata 表结构
        print("\n=== embedding_metadata 表结构 ===")
        cursor = conn.execute("PRAGMA table_info(embedding_metadata)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"📝 {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # 3. 查看数据总数
        cursor = conn.execute("SELECT COUNT(*) FROM embedding_metadata")
        total_count = cursor.fetchone()[0]
        print(f"\n📊 embedding_metadata 总记录数: {total_count}")
        
        # 4. 查看具体的数据样本
        print("\n=== embedding_metadata 数据样本 ===")
        cursor = conn.execute("""
            SELECT id, key, string_value, int_value, float_value
            FROM embedding_metadata 
            ORDER BY id, key
            LIMIT 20
        """)
        
        records = cursor.fetchall()
        current_id = None
        for record in records:
            id_, key, string_value, int_value, float_value = record
            
            if id_ != current_id:
                print(f"\n🔢 ID: {id_}")
                current_id = id_
            
            # 确定实际值
            value = string_value or int_value or float_value or "NULL"
            print(f"  📌 {key}: {value}")
        
        # 5. 检查是否有重复的 document_id, doc_id, ref_doc_id
        print("\n=== 检查 ID 字段的重复情况 ===")
        
        # 检查每个 embedding ID 对应的三个字段
        cursor = conn.execute("""
            SELECT 
                em1.id as embedding_id,
                em1.string_value as document_id,
                em2.string_value as doc_id,
                em3.string_value as ref_doc_id
            FROM embedding_metadata em1
            LEFT JOIN embedding_metadata em2 ON em1.id = em2.id AND em2.key = 'doc_id'
            LEFT JOIN embedding_metadata em3 ON em1.id = em3.id AND em3.key = 'ref_doc_id'
            WHERE em1.key = 'document_id'
            ORDER BY em1.id
            LIMIT 10
        """)
        
        id_records = cursor.fetchall()
        print("🔍 前10个记录的ID字段对比:")
        for record in id_records:
            embedding_id, document_id, doc_id, ref_doc_id = record
            print(f"  Embedding ID: {embedding_id}")
            print(f"    document_id: {document_id}")
            print(f"    doc_id: {doc_id}")
            print(f"    ref_doc_id: {ref_doc_id}")
            
            # 检查是否相同
            if document_id == doc_id == ref_doc_id:
                print(f"    ✅ 三个ID相同")
            else:
                print(f"    ❌ 三个ID不同")
            print()
        
        # 6. 统计每种 key 的数量
        print("=== 各种 key 的统计 ===")
        cursor = conn.execute("""
            SELECT key, COUNT(*) as count
            FROM embedding_metadata 
            GROUP BY key
            ORDER BY count DESC
        """)
        
        key_stats = cursor.fetchall()
        for key, count in key_stats:
            print(f"📊 {key}: {count} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_embedding_metadata()
