#!/usr/bin/env python3
"""
调试 chunk_index 问题
"""
import sqlite3
import json

def debug_chunk_index():
    """调试 chunk_index 问题"""
    print("🔍 调试 chunk_index 问题")
    print("=" * 60)
    
    conn = sqlite3.connect('storage/docstore.db')
    
    # 获取一个文档的详细信息
    cursor = conn.execute("""
        SELECT doc_id, data, chunk_index, file_name 
        FROM documents 
        LIMIT 3
    """)
    
    for row in cursor.fetchall():
        doc_id, data_json, db_chunk_index, file_name = row
        
        print(f"\n📄 文档: {doc_id[:8]}... ({file_name})")
        print(f"  数据库中的 chunk_index: {db_chunk_index}")
        
        # 解析 data 字段
        try:
            data = json.loads(data_json)
            
            # 检查 data 中的 metadata
            if 'metadata' in data:
                metadata = data['metadata']
                data_chunk_index = metadata.get('chunk_index', 'None')
                print(f"  data.metadata 中的 chunk_index: {data_chunk_index}")
                
                # 显示所有 metadata 字段
                print(f"  data.metadata 字段:")
                for key, value in metadata.items():
                    if isinstance(value, str) and len(value) > 50:
                        print(f"    {key}: {value[:50]}...")
                    else:
                        print(f"    {key}: {value}")
            else:
                print(f"  data 中没有 metadata")
                
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON 解析失败: {e}")
    
    conn.close()

def check_node_creation():
    """检查节点创建过程"""
    print("\n🔧 模拟节点创建过程")
    print("=" * 60)
    
    # 模拟 main.py 中的逻辑
    print("模拟代码:")
    print("""
    for chunk_index, node in enumerate(nodes):
        node.metadata.update({
            'file_id': file_id,
            'file_name': file.filename,
            'chunk_index': chunk_index + 1  # 这里设置为 1, 2, 3...
        })
    
    # 然后调用
    storage_context.docstore.add_documents(nodes)  # 没有传递 file_metadata
    """)
    
    print("\n在 add_documents 方法中:")
    print("""
    metadata = file_metadata or {}  # file_metadata 是 None，所以 metadata = {}
    if hasattr(node, 'metadata') and node.metadata:
        metadata.update(node.metadata)  # 这里应该会更新 chunk_index
    
    chunk_index = metadata.get('chunk_index')  # 应该能获取到正确的值
    """)
    
    print("\n🤔 问题可能在于:")
    print("1. node.metadata 没有正确设置")
    print("2. metadata.update() 没有正确执行")
    print("3. 数据库插入时 chunk_index 被覆盖")

def main():
    debug_chunk_index()
    check_node_creation()

if __name__ == "__main__":
    main()
