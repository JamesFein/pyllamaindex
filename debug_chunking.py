#!/usr/bin/env python3
"""
调试文档分块问题
"""
import os
import sqlite3
import json
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

def debug_chunking_process():
    """调试文档分块过程"""
    print("🔍 调试文档分块过程")
    print("=" * 60)
    
    # 1. 读取原始文档
    data_dir = os.environ.get("DATA_DIR", "data")
    reader = SimpleDirectoryReader(data_dir, recursive=True)
    documents = reader.load_data()
    
    print(f"📄 读取到 {len(documents)} 个文档:")
    for i, doc in enumerate(documents):
        print(f"  {i+1}. {doc.metadata.get('file_name', 'Unknown')} - {len(doc.text)} 字符")
        print(f"     内容预览: {doc.text[:100]}...")
        print(f"     doc_id: {doc.doc_id}")
        print()
    
    # 2. 测试分块器
    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents(documents)
    
    print(f"🧩 分块结果: {len(nodes)} 个节点")
    print()
    
    # 3. 按文档分组分析
    doc_groups = {}
    for node in nodes:
        ref_doc_id = node.ref_doc_id
        if ref_doc_id not in doc_groups:
            doc_groups[ref_doc_id] = []
        doc_groups[ref_doc_id].append(node)
    
    print("📊 按文档分组的节点:")
    for doc_id, doc_nodes in doc_groups.items():
        # 找到对应的原始文档
        original_doc = next((d for d in documents if d.doc_id == doc_id), None)
        file_name = original_doc.metadata.get('file_name', 'Unknown') if original_doc else 'Unknown'
        
        print(f"📄 {file_name} (doc_id: {doc_id[:20]}...):")
        print(f"   原始文档长度: {len(original_doc.text) if original_doc else 'Unknown'} 字符")
        print(f"   分块数量: {len(doc_nodes)}")
        
        for i, node in enumerate(doc_nodes):
            print(f"   块 {i}: {len(node.text)} 字符 - {node.text[:50]}...")
            print(f"        node_id: {node.node_id[:20]}...")
        print()

def check_database_vs_actual():
    """对比数据库中的数据和实际分块结果"""
    print("🔍 对比数据库数据和实际分块")
    print("=" * 60)
    
    # 检查数据库中的数据
    with sqlite3.connect('storage/docstore.db') as conn:
        cursor = conn.execute('''
            SELECT file_name, COUNT(*) as db_chunks,
                   COUNT(DISTINCT LENGTH(data)) as unique_lengths,
                   MIN(LENGTH(data)) as min_length,
                   MAX(LENGTH(data)) as max_length
            FROM documents 
            GROUP BY file_name
        ''')
        
        print("📊 数据库中的数据:")
        print("文件名                | 块数 | 唯一长度数 | 最小长度 | 最大长度")
        print("-" * 70)
        
        for row in cursor.fetchall():
            file_name, db_chunks, unique_lengths, min_length, max_length = row
            print(f"{file_name:<20} | {db_chunks:<4} | {unique_lengths:<10} | {min_length:<8} | {max_length}")
        
        print()
        
        # 检查是否有相同内容的块
        cursor = conn.execute('''
            SELECT file_name, data, COUNT(*) as count
            FROM documents 
            GROUP BY file_name, data
            HAVING COUNT(*) > 1
        ''')
        
        duplicates = cursor.fetchall()
        if duplicates:
            print("⚠️  发现重复的文档块:")
            for file_name, data, count in duplicates:
                content_preview = json.loads(data).get('text', '')[:100] if data else ''
                print(f"  {file_name}: {count} 个相同的块 - {content_preview}...")
        else:
            print("✅ 没有发现重复的文档块")

def analyze_chunk_index_logic():
    """分析 chunk_index 逻辑"""
    print(f"\n🔍 分析 chunk_index 逻辑问题")
    print("=" * 60)
    
    print("📋 generate.py 中的逻辑:")
    print("1. 读取所有文档")
    print("2. 使用 SentenceSplitter 分块")
    print("3. 为每个文档找到对应的节点: doc_nodes = [node for node in nodes if node.ref_doc_id == document.doc_id]")
    print("4. 为每个节点分配 chunk_index: 'chunk_index': i")
    
    print(f"\n🤔 可能的问题:")
    print("1. 如果文档没有被正确分块，每个文档只有一个节点")
    print("2. 重复运行导致相同内容被多次添加")
    print("3. 数据库中的 chunk_index 都是 0，说明每个文档组只有一个节点")
    
    print(f"\n💡 验证方法:")
    print("1. 检查实际的分块结果")
    print("2. 确认是否真的有多个块")
    print("3. 检查重复数据的来源")

def suggest_solution():
    """建议解决方案"""
    print(f"\n💡 解决方案")
    print("=" * 60)
    
    print("🔧 立即解决:")
    print("1. 重置数据库清除重复数据")
    print("2. 检查文档分块设置")
    print("3. 确保 generate 只运行一次")
    
    print(f"\n🔧 长期改进:")
    print("1. 添加去重逻辑，避免重复处理相同文档")
    print("2. 改进 chunk_index 的计算和验证")
    print("3. 添加数据一致性检查")

def main():
    """主调试流程"""
    debug_chunking_process()
    check_database_vs_actual()
    analyze_chunk_index_logic()
    suggest_solution()

if __name__ == "__main__":
    main()
