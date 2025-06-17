#!/usr/bin/env python3
"""
修复 ChromaDB ID 映射错误问题
"""

import sqlite3
import json
import os
import logging
from typing import List, Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_current_state():
    """分析当前状态"""
    print("🔍 分析当前 ChromaDB ID 映射状态")
    print("=" * 60)
    
    # 1. 检查 DocStore 数据
    docstore_path = 'storage/docstore.db'
    docstore_nodes = {}
    
    if os.path.exists(docstore_path):
        conn = sqlite3.connect(docstore_path)
        cursor = conn.execute("SELECT doc_id, data FROM documents")
        
        for doc_id, data in cursor.fetchall():
            try:
                node_data = json.loads(data)
                docstore_nodes[doc_id] = {
                    'node_id': node_data.get('id_', doc_id),
                    'ref_doc_id': node_data.get('ref_doc_id'),
                    'relationships': node_data.get('relationships', {}),
                    'metadata': node_data.get('metadata', {})
                }
            except json.JSONDecodeError:
                logger.warning(f"无法解析节点数据: {doc_id}")
        
        conn.close()
        print(f"📄 DocStore 中有 {len(docstore_nodes)} 个节点")
    
    # 2. 检查 ChromaDB 数据
    chroma_path = 'storage/chroma_db_new/chroma.sqlite3'
    chroma_nodes = {}
    
    if os.path.exists(chroma_path):
        conn = sqlite3.connect(chroma_path)
        
        # 获取所有 embedding 的元数据
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
        
        for embedding_id, document_id, doc_id, ref_doc_id, file_name, chunk_index in cursor.fetchall():
            chroma_nodes[embedding_id] = {
                'document_id': document_id,
                'doc_id': doc_id,
                'ref_doc_id': ref_doc_id,
                'file_name': file_name,
                'chunk_index': chunk_index
            }
        
        conn.close()
        print(f"🧠 ChromaDB 中有 {len(chroma_nodes)} 个向量")
    
    return docstore_nodes, chroma_nodes

def fix_chromadb_metadata():
    """修复 ChromaDB 元数据"""
    print("\n🔧 开始修复 ChromaDB ID 映射")
    print("=" * 60)
    
    # 1. 分析当前状态
    docstore_nodes, chroma_nodes = analyze_current_state()
    
    if not docstore_nodes or not chroma_nodes:
        print("❌ 无法获取必要的数据，修复失败")
        return False
    
    # 2. 建立映射关系
    print("\n📋 建立正确的 ID 映射关系...")
    
    # 按文件名和chunk_index建立映射
    file_chunk_to_docstore = {}
    for doc_id, node_info in docstore_nodes.items():
        metadata = node_info['metadata']
        file_name = metadata.get('file_name', 'unknown')
        chunk_index = metadata.get('chunk_index', 0)
        key = f"{file_name}_chunk_{chunk_index}"
        file_chunk_to_docstore[key] = {
            'correct_doc_id': node_info['node_id'],
            'ref_doc_id': node_info['ref_doc_id'],
            'relationships': node_info['relationships']
        }
    
    # 3. 准备修复数据
    fixes_needed = []
    
    for embedding_id, chroma_info in chroma_nodes.items():
        file_name = chroma_info['file_name']
        chunk_index = chroma_info['chunk_index']
        key = f"{file_name}_chunk_{chunk_index}"
        
        if key in file_chunk_to_docstore:
            docstore_info = file_chunk_to_docstore[key]
            correct_doc_id = docstore_info['correct_doc_id']
            current_doc_id = chroma_info['doc_id']
            
            if current_doc_id != correct_doc_id:
                fixes_needed.append({
                    'embedding_id': embedding_id,
                    'current_doc_id': current_doc_id,
                    'correct_doc_id': correct_doc_id,
                    'file_name': file_name,
                    'chunk_index': chunk_index
                })
                print(f"🔍 需要修复: {file_name} chunk_{chunk_index}")
                print(f"   当前 doc_id: {current_doc_id}")
                print(f"   正确 doc_id: {correct_doc_id}")
    
    if not fixes_needed:
        print("✅ 没有发现需要修复的ID映射问题")
        return True
    
    # 4. 执行修复
    print(f"\n🛠️  开始修复 {len(fixes_needed)} 个错误的ID映射...")
    
    chroma_path = 'storage/chroma_db_new/chroma.sqlite3'
    conn = sqlite3.connect(chroma_path)
    
    try:
        for fix in fixes_needed:
            embedding_id = fix['embedding_id']
            correct_doc_id = fix['correct_doc_id']
            
            # 更新 doc_id 字段
            conn.execute("""
                UPDATE embedding_metadata 
                SET string_value = ? 
                WHERE id = ? AND key = 'doc_id'
            """, (correct_doc_id, embedding_id))
            
            print(f"✅ 修复了 embedding {embedding_id} 的 doc_id")
        
        conn.commit()
        print(f"🎉 成功修复了 {len(fixes_needed)} 个ID映射错误")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 修复过程中出错: {e}")
        return False
    finally:
        conn.close()
    
    return True

def verify_fix():
    """验证修复结果"""
    print("\n🔍 验证修复结果")
    print("=" * 60)
    
    chroma_path = 'storage/chroma_db_new/chroma.sqlite3'
    if not os.path.exists(chroma_path):
        print("❌ ChromaDB 文件不存在")
        return False
    
    conn = sqlite3.connect(chroma_path)
    
    # 检查是否还有相同的 document_id, doc_id, ref_doc_id
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
    
    all_correct = True
    
    for embedding_id, document_id, doc_id, ref_doc_id, file_name, chunk_index in cursor.fetchall():
        print(f"\n📊 {file_name} chunk_{chunk_index}:")
        print(f"   document_id: {document_id}")
        print(f"   doc_id:      {doc_id}")
        print(f"   ref_doc_id:  {ref_doc_id}")
        
        if document_id == doc_id == ref_doc_id:
            print("   ❌ 三个ID仍然相同 (问题未解决)")
            all_correct = False
        elif document_id == ref_doc_id and doc_id != document_id:
            print("   ✅ ID映射正确")
        else:
            print("   ⚠️  ID关系异常")
            all_correct = False
    
    conn.close()
    
    if all_correct:
        print("\n🎉 所有ID映射都已正确修复！")
    else:
        print("\n❌ 仍有ID映射问题需要解决")
    
    return all_correct

def main():
    """主函数"""
    print("🚀 ChromaDB ID 映射修复工具")
    print("=" * 60)
    
    # 1. 分析当前状态
    analyze_current_state()
    
    # 2. 执行修复
    if fix_chromadb_metadata():
        # 3. 验证修复结果
        verify_fix()
    else:
        print("❌ 修复失败")

if __name__ == "__main__":
    main()
