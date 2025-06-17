#!/usr/bin/env python3
"""
分析 LlamaIndex 中 document_id, doc_id, ref_doc_id 的关系
"""

import sqlite3
import json
import os

def analyze_id_relationship():
    """分析ID关系"""
    print("🔍 分析 LlamaIndex ID 关系")
    print("=" * 60)
    
    # 1. 检查 docstore.db 中的数据
    docstore_path = 'storage/docstore.db'
    if os.path.exists(docstore_path):
        print("\n=== DocStore 数据分析 ===")
        conn = sqlite3.connect(docstore_path)
        
        # 查看 documents 表
        cursor = conn.execute("SELECT doc_id, file_name, chunk_index FROM documents ORDER BY file_name, chunk_index")
        doc_records = cursor.fetchall()
        
        print("📄 Documents 表中的记录:")
        for doc_id, file_name, chunk_index in doc_records:
            print(f"  📝 {file_name} - chunk_{chunk_index}: {doc_id}")
        
        conn.close()
    
    # 2. 检查 ChromaDB 中的数据
    chroma_path = 'storage/chroma_db_new/chroma.sqlite3'
    if os.path.exists(chroma_path):
        print("\n=== ChromaDB 数据分析 ===")
        conn = sqlite3.connect(chroma_path)
        
        # 获取所有 embedding 的 ID 信息
        cursor = conn.execute("""
            SELECT 
                em1.id as embedding_id,
                em1.string_value as document_id,
                em2.string_value as doc_id,
                em3.string_value as ref_doc_id,
                em4.string_value as file_name,
                em5.int_value as chunk_index
            FROM embedding_metadata em1
            LEFT JOIN embedding_metadata em2 ON em1.id = em2.id AND em2.key = 'doc_id'
            LEFT JOIN embedding_metadata em3 ON em1.id = em3.id AND em3.key = 'ref_doc_id'
            LEFT JOIN embedding_metadata em4 ON em1.id = em4.id AND em4.key = 'file_name'
            LEFT JOIN embedding_metadata em5 ON em1.id = em5.id AND em5.key = 'chunk_index'
            WHERE em1.key = 'document_id'
            ORDER BY em4.string_value, em5.int_value
        """)
        
        chroma_records = cursor.fetchall()
        print("🧠 ChromaDB 中的 ID 关系:")
        
        for record in chroma_records:
            embedding_id, document_id, doc_id, ref_doc_id, file_name, chunk_index = record
            print(f"\n  📊 Embedding #{embedding_id} - {file_name} chunk_{chunk_index}")
            print(f"    document_id: {document_id}")
            print(f"    doc_id:      {doc_id}")
            print(f"    ref_doc_id:  {ref_doc_id}")
            
            # 分析关系
            if document_id == doc_id == ref_doc_id:
                print(f"    ✅ 三个ID完全相同")
            elif document_id == ref_doc_id and doc_id != document_id:
                print(f"    🔄 document_id = ref_doc_id, doc_id 不同 (正常情况)")
            else:
                print(f"    ❓ 异常的ID关系")
        
        conn.close()
    
    print("\n" + "=" * 60)
    print("📚 LlamaIndex ID 设计说明:")
    print("1. document_id: 原始文档的唯一标识")
    print("2. doc_id: 文档块(chunk)的唯一标识")  
    print("3. ref_doc_id: 该块所引用的原始文档ID")
    print()
    print("🎯 正常情况下:")
    print("- document_id = ref_doc_id (都指向同一个原始文档)")
    print("- doc_id 应该是每个块的唯一ID")
    print("- 如果三个ID相同，说明每个文档只有一个块")
    print()
    print("🤔 你的情况:")
    print("- 三个ID相同表明每个文档只被分成了一个块")
    print("- 这可能是因为文档太短，或者分块设置导致的")
    print("- 这不是错误，而是正常的设计行为")

if __name__ == "__main__":
    analyze_id_relationship()
