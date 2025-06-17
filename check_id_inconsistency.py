#!/usr/bin/env python3
"""
检查 DocStore 和 ChromaDB 之间的 ID 不一致问题
"""

import sqlite3
import os

def check_id_inconsistency():
    """检查ID不一致问题"""
    print("🚨 检查 DocStore 和 ChromaDB 之间的 ID 不一致问题")
    print("=" * 70)
    
    # 1. 从 DocStore 获取数据
    docstore_path = 'storage/docstore.db'
    docstore_ids = {}
    
    if os.path.exists(docstore_path):
        conn = sqlite3.connect(docstore_path)
        cursor = conn.execute("SELECT doc_id, file_name, chunk_index FROM documents ORDER BY file_name, chunk_index")
        
        for doc_id, file_name, chunk_index in cursor.fetchall():
            key = f"{file_name}_chunk_{chunk_index}"
            docstore_ids[key] = doc_id
            
        conn.close()
    
    # 2. 从 ChromaDB 获取数据
    chroma_path = 'storage/chroma_db_new/chroma.sqlite3'
    chroma_ids = {}
    
    if os.path.exists(chroma_path):
        conn = sqlite3.connect(chroma_path)
        cursor = conn.execute("""
            SELECT 
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
        
        for document_id, doc_id, ref_doc_id, file_name, chunk_index in cursor.fetchall():
            key = f"{file_name}_chunk_{chunk_index}"
            chroma_ids[key] = {
                'document_id': document_id,
                'doc_id': doc_id,
                'ref_doc_id': ref_doc_id
            }
            
        conn.close()
    
    # 3. 对比分析
    print("📊 DocStore vs ChromaDB ID 对比:")
    print()
    
    for key in sorted(set(docstore_ids.keys()) | set(chroma_ids.keys())):
        print(f"🔍 {key}:")
        
        if key in docstore_ids:
            docstore_id = docstore_ids[key]
            print(f"  📄 DocStore ID:    {docstore_id}")
        else:
            print(f"  📄 DocStore ID:    ❌ 不存在")
            
        if key in chroma_ids:
            chroma_data = chroma_ids[key]
            print(f"  🧠 ChromaDB IDs:")
            print(f"     document_id:   {chroma_data['document_id']}")
            print(f"     doc_id:        {chroma_data['doc_id']}")
            print(f"     ref_doc_id:    {chroma_data['ref_doc_id']}")
            
            # 检查一致性
            if key in docstore_ids:
                docstore_id = docstore_ids[key]
                if docstore_id == chroma_data['doc_id']:
                    print(f"  ✅ DocStore ID = ChromaDB doc_id")
                else:
                    print(f"  ❌ DocStore ID ≠ ChromaDB doc_id")
                    print(f"     DocStore:   {docstore_id}")
                    print(f"     ChromaDB:   {chroma_data['doc_id']}")
                    
                # 检查 ChromaDB 内部一致性
                if (chroma_data['document_id'] == chroma_data['doc_id'] == chroma_data['ref_doc_id']):
                    print(f"  ⚠️  ChromaDB 三个ID完全相同 (可能有问题)")
                elif chroma_data['document_id'] == chroma_data['ref_doc_id']:
                    print(f"  ✅ ChromaDB document_id = ref_doc_id (正常)")
                else:
                    print(f"  ❌ ChromaDB ID关系异常")
        else:
            print(f"  🧠 ChromaDB IDs:   ❌ 不存在")
            
        print()
    
    print("=" * 70)
    print("🎯 问题分析:")
    print("1. DocStore 中每个 chunk 都有唯一的 doc_id")
    print("2. ChromaDB 中的 document_id, doc_id, ref_doc_id 都相同")
    print("3. 这表明 ChromaDB 中存储的不是 chunk 的 ID，而是原始文档的 ID")
    print()
    print("💡 可能的原因:")
    print("1. 在向量化过程中，chunk 的 ID 被错误地设置为文档 ID")
    print("2. LlamaIndex 的某个版本或配置导致了这个问题")
    print("3. 需要检查向量化代码中的 ID 设置逻辑")

if __name__ == "__main__":
    check_id_inconsistency()
