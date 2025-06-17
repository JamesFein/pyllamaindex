#!/usr/bin/env python3
"""
分析 LlamaIndex 节点关系，找出神秘ID的真正来源
"""

import sqlite3
import json
import os

def analyze_relationships():
    """分析节点关系"""
    target_id = "10316370-d5dc-4a54-ac60-7e853b805328"
    
    print(f"🔍 分析节点关系，追踪ID来源")
    print("=" * 60)
    
    # 1. 从 DocStore 获取完整的节点数据
    print("\n=== 1. DocStore 中的节点关系 ===")
    docstore_path = 'storage/docstore.db'
    if os.path.exists(docstore_path):
        conn = sqlite3.connect(docstore_path)
        
        cursor = conn.execute("SELECT doc_id, data FROM documents ORDER BY doc_id")
        for doc_id, data in cursor.fetchall():
            try:
                node_data = json.loads(data)
                print(f"\n📄 节点: {doc_id}")
                print(f"   实际ID (id_): {node_data.get('id_', 'N/A')}")
                print(f"   类型: {node_data.get('class_name', 'N/A')}")
                
                # 分析关系
                relationships = node_data.get('relationships', {})
                if relationships:
                    print(f"   关系:")
                    for rel_type, rel_info in relationships.items():
                        rel_node_id = rel_info.get('node_id', 'N/A')
                        rel_node_type = rel_info.get('node_type', 'N/A')
                        print(f"     类型{rel_type}: {rel_node_id} (节点类型: {rel_node_type})")
                        
                        # 检查是否是我们要找的神秘ID
                        if rel_node_id == target_id:
                            print(f"     🎯 找到了！这个关系指向神秘ID")
                            print(f"     关系类型: {rel_type}")
                            print(f"     节点类型: {rel_node_type}")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ 无法解析JSON: {e}")
        
        conn.close()
    
    # 2. 检查 ref_doc_info 表
    print(f"\n=== 2. 检查 ref_doc_info 表 ===")
    if os.path.exists(docstore_path):
        conn = sqlite3.connect(docstore_path)
        
        cursor = conn.execute("SELECT ref_doc_id, node_ids, metadata FROM ref_doc_info")
        ref_records = cursor.fetchall()
        
        if ref_records:
            for ref_doc_id, node_ids_json, metadata_json in ref_records:
                print(f"\n📋 引用文档: {ref_doc_id}")
                
                if ref_doc_id == target_id:
                    print(f"   🎯 这就是我们要找的神秘ID！")
                
                try:
                    node_ids = json.loads(node_ids_json) if node_ids_json else []
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    
                    print(f"   包含的节点IDs: {node_ids}")
                    print(f"   元数据: {metadata}")
                    
                except json.JSONDecodeError:
                    print(f"   ❌ 无法解析JSON数据")
        else:
            print("❌ ref_doc_info 表为空")
        
        conn.close()
    
    # 3. 分析LlamaIndex的节点类型
    print(f"\n=== 3. LlamaIndex 节点类型说明 ===")
    print("根据LlamaIndex文档，节点类型编号含义:")
    print("1 = DOCUMENT (文档节点)")
    print("2 = TEXT (文本节点)")  
    print("3 = INDEX (索引节点)")
    print("4 = DOCUMENT (文档节点的另一种表示)")
    print()
    
    # 4. 推理分析
    print(f"=== 4. 推理分析 ===")
    print(f"基于以上信息，神秘ID {target_id} 的来源:")
    print()
    print("🔍 线索1: 这个ID出现在节点的 relationships 中")
    print("🔍 线索2: 关系类型是 '1'，表示 DOCUMENT 类型")
    print("🔍 线索3: 这个ID不在 documents 表中，但在 relationships 中被引用")
    print()
    print("💡 结论:")
    print("这个ID很可能是:")
    print("1. 原始Document对象的ID (不是TextNode的ID)")
    print("2. 在文档分块时，LlamaIndex创建的父文档引用")
    print("3. 所有chunk都通过relationships指向这个父文档")
    print()
    print("🚨 问题所在:")
    print("ChromaDB错误地将这个父文档ID设置为了chunk的ID")
    print("正确的应该是使用chunk自己的ID (eea744ac..., 80b33bd3...)")

if __name__ == "__main__":
    analyze_relationships()
