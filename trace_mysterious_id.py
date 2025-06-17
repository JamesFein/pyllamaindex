#!/usr/bin/env python3
"""
追踪神秘ID 10316370-d5dc-4a54-ac60-7e853b805328 的来源
"""

import sqlite3
import json
import os

def trace_mysterious_id():
    """追踪神秘ID的来源"""
    target_id = "10316370-d5dc-4a54-ac60-7e853b805328"
    
    print(f"🔍 追踪神秘ID: {target_id}")
    print("=" * 80)
    
    # 1. 检查 DocStore 中是否有这个ID
    print("\n=== 1. 检查 DocStore ===")
    docstore_path = 'storage/docstore.db'
    if os.path.exists(docstore_path):
        conn = sqlite3.connect(docstore_path)
        
        # 检查 documents 表
        cursor = conn.execute("SELECT * FROM documents WHERE doc_id = ?", (target_id,))
        doc_result = cursor.fetchone()
        if doc_result:
            print(f"✅ 在 documents 表中找到: {doc_result}")
        else:
            print(f"❌ 在 documents 表中未找到")
        
        # 检查 ref_doc_info 表
        cursor = conn.execute("SELECT * FROM ref_doc_info WHERE ref_doc_id = ?", (target_id,))
        ref_result = cursor.fetchone()
        if ref_result:
            print(f"✅ 在 ref_doc_info 表中找到:")
            print(f"   ref_doc_id: {ref_result[0]}")
            print(f"   node_ids: {ref_result[1]}")
            print(f"   metadata: {ref_result[2]}")
        else:
            print(f"❌ 在 ref_doc_info 表中未找到")
        
        # 检查所有包含这个ID的地方
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            try:
                cursor = conn.execute(f"SELECT * FROM {table}")
                columns = [description[0] for description in cursor.description]
                
                # 检查每一行是否包含目标ID
                cursor = conn.execute(f"SELECT * FROM {table}")
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    for col, value in row_dict.items():
                        if str(value) == target_id:
                            print(f"✅ 在表 {table}.{col} 中找到: {value}")
                        elif isinstance(value, str) and target_id in value:
                            print(f"🔍 在表 {table}.{col} 中部分匹配: {value[:100]}...")
            except Exception as e:
                print(f"⚠️  检查表 {table} 时出错: {e}")
        
        conn.close()
    
    # 2. 检查 ChromaDB 中的详细信息
    print("\n=== 2. 检查 ChromaDB 详细信息 ===")
    chroma_path = 'storage/chroma_db_new/chroma.sqlite3'
    if os.path.exists(chroma_path):
        conn = sqlite3.connect(chroma_path)
        
        # 查找包含这个ID的所有记录
        cursor = conn.execute("""
            SELECT id, key, string_value, int_value, float_value
            FROM embedding_metadata 
            WHERE string_value = ?
            ORDER BY id, key
        """, (target_id,))
        
        records = cursor.fetchall()
        if records:
            print(f"✅ 在 ChromaDB 中找到 {len(records)} 条记录:")
            current_id = None
            for record in records:
                id_, key, string_value, int_value, float_value = record
                if id_ != current_id:
                    print(f"\n  📊 Embedding ID: {id_}")
                    current_id = id_
                print(f"    {key}: {string_value or int_value or float_value}")
        else:
            print(f"❌ 在 ChromaDB 中未找到")
        
        # 查看这个ID对应的完整节点内容
        cursor = conn.execute("""
            SELECT em.string_value as node_content
            FROM embedding_metadata em
            WHERE em.key = '_node_content' 
            AND em.id IN (
                SELECT id FROM embedding_metadata 
                WHERE key = 'document_id' AND string_value = ?
            )
        """, (target_id,))
        
        node_contents = cursor.fetchall()
        if node_contents:
            print(f"\n🔍 对应的节点内容:")
            for i, (content,) in enumerate(node_contents):
                try:
                    node_data = json.loads(content)
                    print(f"\n  节点 {i+1}:")
                    print(f"    id_: {node_data.get('id_', 'N/A')}")
                    print(f"    class_name: {node_data.get('class_name', 'N/A')}")
                    if 'relationships' in node_data:
                        print(f"    relationships: {list(node_data['relationships'].keys())}")
                        for rel_key, rel_data in node_data['relationships'].items():
                            print(f"      {rel_key}: {rel_data.get('node_id', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"    ⚠️  无法解析JSON内容")
        
        conn.close()
    
    # 3. 分析ID的格式和可能来源
    print(f"\n=== 3. ID 格式分析 ===")
    print(f"目标ID: {target_id}")
    print(f"长度: {len(target_id)} 字符")
    print(f"格式: {target_id.count('-')} 个连字符")
    
    # 检查是否是UUID格式
    import re
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if re.match(uuid_pattern, target_id):
        print("✅ 符合UUID格式")
    else:
        print("❌ 不符合标准UUID格式")
    
    # 4. 检查是否在代码中硬编码
    print(f"\n=== 4. 检查代码中的引用 ===")
    print("搜索当前目录中是否有这个ID...")
    
    import glob
    python_files = glob.glob("*.py")
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if target_id in content:
                    print(f"✅ 在文件 {file_path} 中找到")
        except Exception as e:
            pass
    
    print(f"\n=== 5. 总结 ===")
    print("这个ID可能的来源:")
    print("1. LlamaIndex自动生成的Document ID")
    print("2. 在文档加载时被设置的原始文档ID")
    print("3. 某个配置或代码中硬编码的值")
    print("4. 数据库迁移或重建过程中产生的ID")

if __name__ == "__main__":
    trace_mysterious_id()
