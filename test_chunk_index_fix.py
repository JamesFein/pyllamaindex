#!/usr/bin/env python3
"""
直接测试 chunk_index 修复
"""
import os
import hashlib
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from app.storage_config import get_storage_context
from app.index import STORAGE_DIR

def test_node_creation():
    """测试节点创建过程"""
    print("🧪 测试节点创建过程")
    print("=" * 60)
    
    # 创建测试文件
    test_content = """测试文档

这是第一段内容，用于测试文档分块功能。

这是第二段内容，应该被分成不同的块。

这是第三段内容，每个块都应该有正确的索引。"""
    
    test_file = "test_chunk_index.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        # 1. 读取文档
        reader = SimpleDirectoryReader(input_files=[test_file])
        documents = reader.load_data()
        print(f"📄 读取到 {len(documents)} 个文档")
        
        # 2. 解析为节点
        parser = SentenceSplitter(chunk_size=100, chunk_overlap=20)
        nodes = parser.get_nodes_from_documents(documents)
        print(f"🧩 分成 {len(nodes)} 个节点")
        
        # 3. 为每个节点添加元数据（模拟 main.py 的逻辑）
        file_id = f"file_{hashlib.md5(test_file.encode()).hexdigest()[:8]}"
        
        for chunk_index, node in enumerate(nodes):
            print(f"\n📝 处理节点 {chunk_index + 1}:")
            print(f"  节点ID: {node.node_id}")
            print(f"  原始 metadata: {getattr(node, 'metadata', {})}")
            
            # 添加文件元数据（模拟 main.py 第 307-315 行）
            if hasattr(node, 'metadata'):
                node.metadata.update({
                    'file_id': file_id,
                    'file_name': test_file,
                    'file_size': len(test_content),
                    'file_type': 'text/plain',
                    'chunk_index': chunk_index + 1  # 关键：从1开始
                })
            else:
                node.metadata = {
                    'file_id': file_id,
                    'file_name': test_file,
                    'file_size': len(test_content),
                    'file_type': 'text/plain',
                    'chunk_index': chunk_index + 1  # 关键：从1开始
                }
            
            print(f"  更新后 metadata: {node.metadata}")
            
            # 检查序列化后的数据
            node_dict = node.to_dict()
            serialized_chunk_index = node_dict.get('metadata', {}).get('chunk_index', 'None')
            print(f"  序列化后的 chunk_index: {serialized_chunk_index}")
        
        # 4. 测试存储（如果存储目录存在）
        if os.path.exists(STORAGE_DIR):
            print(f"\n💾 测试存储到数据库")
            storage_context = get_storage_context(STORAGE_DIR)
            
            # 模拟 add_documents 的关键逻辑
            print("模拟 add_documents 逻辑:")
            for i, node in enumerate(nodes):
                file_metadata = None  # 模拟不传递 file_metadata
                
                metadata = file_metadata or {}
                if hasattr(node, 'metadata') and node.metadata:
                    metadata.update(node.metadata)
                
                chunk_index = metadata.get('chunk_index')
                print(f"  节点 {i+1}: 提取的 chunk_index = {chunk_index}")
        else:
            print(f"\n⚠️  存储目录不存在: {STORAGE_DIR}")
            print("无法测试数据库存储")
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 清理测试文件: {test_file}")

def main():
    """主函数"""
    print("🧪 Chunk Index 修复测试")
    print("=" * 80)
    
    test_node_creation()
    
    print("\n💡 测试结论:")
    print("如果序列化后的 chunk_index 正确，但数据库中仍然是0，")
    print("那么问题可能在于:")
    print("1. 数据库中的数据是旧的")
    print("2. add_documents 方法中的逻辑有问题")
    print("3. 需要清理数据库重新测试")

if __name__ == "__main__":
    main()
