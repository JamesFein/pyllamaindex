#!/usr/bin/env python3
"""
简单修复 ChromaDB ID 映射错误
"""

import sqlite3
import json
import os

def main():
    print("🚀 开始修复 ChromaDB ID 映射问题")
    
    # 1. 检查文件是否存在
    docstore_path = 'storage/docstore.db'
    chroma_path = 'storage/chroma_db_new/chroma.sqlite3'
    
    if not os.path.exists(docstore_path):
        print(f"❌ DocStore 文件不存在: {docstore_path}")
        return
    
    if not os.path.exists(chroma_path):
        print(f"❌ ChromaDB 文件不存在: {chroma_path}")
        return
    
    print("✅ 找到必要的数据库文件")
    
    # 2. 从 DocStore 获取正确的映射
    print("📄 读取 DocStore 数据...")
    docstore_mapping = {}
    
    conn = sqlite3.connect(docstore_path)
    cursor = conn.execute("SELECT doc_id, data FROM documents")
    
    for doc_id, data in cursor.fetchall():
        try:
            node_data = json.loads(data)
            metadata = node_data.get('metadata', {})
            file_name = metadata.get('file_name', 'unknown')
            chunk_index = metadata.get('chunk_index', 0)
            
            key = f"{file_name}_chunk_{chunk_index}"
            docstore_mapping[key] = {
                'correct_doc_id': node_data.get('id_', doc_id),
                'file_name': file_name,
                'chunk_index': chunk_index
            }
            print(f"  📝 {key}: {node_data.get('id_', doc_id)}")
            
        except Exception as e:
            print(f"  ⚠️  解析节点 {doc_id} 失败: {e}")
    
    conn.close()
    print(f"✅ 从 DocStore 读取了 {len(docstore_mapping)} 个节点映射")
    
    # 3. 修复 ChromaDB 数据
    print("\n🔧 修复 ChromaDB 数据...")
    conn = sqlite3.connect(chroma_path)
    
    # 获取需要修复的记录
    cursor = conn.execute("""
        SELECT 
            em1.id as embedding_id,
            em2.string_value as current_doc_id,
            em4.string_value as file_name,
            em5.int_value as chunk_index
        FROM embedding_metadata em1
        LEFT JOIN embedding_metadata em2 ON em1.id = em2.id AND em2.key = 'doc_id'
        LEFT JOIN embedding_metadata em4 ON em1.id = em4.id AND em4.key = 'file_name'
        LEFT JOIN embedding_metadata em5 ON em1.id = em5.id AND em5.key = 'chunk_index'
        WHERE em1.key = 'document_id'
    """)
    
    fixes_applied = 0
    
    for embedding_id, current_doc_id, file_name, chunk_index in cursor.fetchall():
        key = f"{file_name}_chunk_{chunk_index}"
        
        if key in docstore_mapping:
            correct_doc_id = docstore_mapping[key]['correct_doc_id']
            
            if current_doc_id != correct_doc_id:
                print(f"  🔧 修复 {key}:")
                print(f"     当前: {current_doc_id}")
                print(f"     正确: {correct_doc_id}")
                
                # 更新 doc_id
                conn.execute("""
                    UPDATE embedding_metadata 
                    SET string_value = ? 
                    WHERE id = ? AND key = 'doc_id'
                """, (correct_doc_id, embedding_id))
                
                fixes_applied += 1
            else:
                print(f"  ✅ {key} 已经正确")
        else:
            print(f"  ⚠️  找不到 {key} 的映射")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 修复完成！应用了 {fixes_applied} 个修复")
    
    # 4. 验证结果
    print("\n🔍 验证修复结果...")
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
    
    all_good = True
    for document_id, doc_id, ref_doc_id, file_name, chunk_index in cursor.fetchall():
        print(f"\n📊 {file_name} chunk_{chunk_index}:")
        print(f"   document_id: {document_id}")
        print(f"   doc_id:      {doc_id}")
        print(f"   ref_doc_id:  {ref_doc_id}")
        
        if document_id == doc_id == ref_doc_id:
            print("   ❌ 三个ID仍然相同")
            all_good = False
        elif document_id == ref_doc_id and doc_id != document_id:
            print("   ✅ ID映射正确")
        else:
            print("   ⚠️  ID关系异常")
    
    conn.close()
    
    if all_good:
        print("\n🎉 所有ID映射都已正确！")
    else:
        print("\n❌ 仍有问题需要解决")

if __name__ == "__main__":
    main()
