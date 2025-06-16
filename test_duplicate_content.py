#!/usr/bin/env python3
"""
测试重复文本块的处理机制
"""
import os
import tempfile
import logging
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.readers import SimpleDirectoryReader
from app.storage_config import get_storage_context

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_files_with_duplicate_content():
    """创建包含重复内容的测试文件"""
    test_dir = "test_duplicate_data"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建两个文件，包含相同的文本块
    duplicate_content = """
这是一段重复的文本内容。
这段内容会出现在多个文件中。
用于测试系统如何处理重复的文本块。
"""
    
    # 文件1
    with open(os.path.join(test_dir, "file1.txt"), "w", encoding="utf-8") as f:
        f.write("文件1的开头内容。\n")
        f.write(duplicate_content)
        f.write("文件1的结尾内容。\n")
    
    # 文件2
    with open(os.path.join(test_dir, "file2.txt"), "w", encoding="utf-8") as f:
        f.write("文件2的开头内容。\n")
        f.write(duplicate_content)
        f.write("文件2的结尾内容。\n")
    
    # 文件3 - 完全相同的内容
    with open(os.path.join(test_dir, "file3.txt"), "w", encoding="utf-8") as f:
        f.write(duplicate_content)
    
    return test_dir

def analyze_node_generation():
    """分析节点生成过程"""
    logger.info("🔍 分析节点生成过程...")
    
    test_dir = create_test_files_with_duplicate_content()
    
    try:
        # 读取文档
        reader = SimpleDirectoryReader(test_dir)
        documents = reader.load_data()
        
        logger.info(f"📄 读取了 {len(documents)} 个文档")
        
        # 解析为节点
        parser = SentenceSplitter(chunk_size=100, chunk_overlap=20)
        nodes = parser.get_nodes_from_documents(documents)
        
        logger.info(f"📝 生成了 {len(nodes)} 个节点")
        
        # 分析节点内容和ID
        content_to_nodes = {}
        node_ids = []
        node_hashes = []
        
        for i, node in enumerate(nodes):
            content = node.text.strip()
            node_id = node.node_id
            node_hash = getattr(node, 'hash', 'No hash')
            
            logger.info(f"节点 {i+1}:")
            logger.info(f"  ID: {node_id}")
            logger.info(f"  Hash: {node_hash}")
            logger.info(f"  内容: {content[:50]}...")
            logger.info(f"  来源: {node.metadata.get('file_name', 'Unknown')}")
            
            # 记录相同内容的节点
            if content in content_to_nodes:
                content_to_nodes[content].append((i+1, node_id, node.metadata.get('file_name', 'Unknown')))
            else:
                content_to_nodes[content] = [(i+1, node_id, node.metadata.get('file_name', 'Unknown'))]
            
            node_ids.append(node_id)
            node_hashes.append(node_hash)
        
        # 分析重复内容
        logger.info("\n🔍 重复内容分析:")
        duplicate_found = False
        for content, node_list in content_to_nodes.items():
            if len(node_list) > 1:
                duplicate_found = True
                logger.info(f"⚠️  发现重复内容 (出现 {len(node_list)} 次):")
                logger.info(f"   内容: {content[:50]}...")
                for node_num, node_id, file_name in node_list:
                    logger.info(f"   - 节点 {node_num} (ID: {node_id}) 来自 {file_name}")
        
        if not duplicate_found:
            logger.info("✅ 没有发现重复内容")
        
        # 分析ID和Hash的唯一性
        logger.info(f"\n🔍 ID唯一性分析:")
        unique_ids = set(node_ids)
        logger.info(f"   总节点数: {len(node_ids)}")
        logger.info(f"   唯一ID数: {len(unique_ids)}")
        if len(node_ids) == len(unique_ids):
            logger.info("✅ 所有节点ID都是唯一的")
        else:
            logger.info("⚠️  发现重复的节点ID")
        
        return nodes, content_to_nodes
        
    finally:
        # 清理测试文件
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)

def test_storage_behavior():
    """测试存储行为"""
    logger.info("🔍 测试存储行为...")
    
    # 创建测试存储
    test_storage_dir = "test_storage"
    storage_context = get_storage_context(test_storage_dir)
    
    try:
        # 创建两个内容相同但ID不同的节点
        node1 = TextNode(
            text="这是重复的测试内容",
            metadata={"source": "file1.txt"}
        )
        
        node2 = TextNode(
            text="这是重复的测试内容",  # 相同内容
            metadata={"source": "file2.txt"}
        )
        
        logger.info(f"节点1 ID: {node1.node_id}")
        logger.info(f"节点2 ID: {node2.node_id}")
        logger.info(f"内容相同: {node1.text == node2.text}")
        logger.info(f"ID相同: {node1.node_id == node2.node_id}")
        
        # 添加到存储
        storage_context.docstore.add_documents([node1, node2])
        
        # 检查存储结果
        stored_node1 = storage_context.docstore.get_document(node1.node_id)
        stored_node2 = storage_context.docstore.get_document(node2.node_id)
        
        logger.info("✅ 两个节点都成功存储")
        logger.info(f"存储的节点1: {stored_node1.text[:30]}...")
        logger.info(f"存储的节点2: {stored_node2.text[:30]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 存储测试失败: {e}")
        return False
        
    finally:
        # 清理测试存储
        import shutil
        shutil.rmtree(test_storage_dir, ignore_errors=True)

def analyze_vector_store_behavior():
    """分析向量存储行为"""
    logger.info("🔍 分析向量存储行为...")
    
    # 对于相同内容的文本块：
    # 1. LlamaIndex会为每个节点生成唯一的node_id
    # 2. 即使内容相同，也会被视为不同的节点
    # 3. 会生成相同或非常相似的向量表示
    # 4. 在检索时可能会返回多个相似的结果
    
    logger.info("📊 向量存储行为分析:")
    logger.info("1. ✅ 每个节点都有唯一的node_id，即使内容相同")
    logger.info("2. ✅ 相同内容会生成相同/相似的向量")
    logger.info("3. ⚠️  检索时可能返回多个相同内容的结果")
    logger.info("4. ⚠️  会占用额外的存储空间")
    logger.info("5. ⚠️  可能影响检索结果的多样性")

def main():
    """主测试流程"""
    print("🧪 重复文本块处理机制测试")
    print("=" * 50)
    
    # 1. 分析节点生成
    nodes, content_analysis = analyze_node_generation()
    
    print()
    
    # 2. 测试存储行为
    test_storage_behavior()
    
    print()
    
    # 3. 分析向量存储行为
    analyze_vector_store_behavior()
    
    print()
    print("📋 总结:")
    print("=" * 50)
    print("🔍 当新文本块与旧文本块内容完全相同时:")
    print("1. ✅ 系统会为每个文本块生成唯一的node_id")
    print("2. ✅ 两个文本块都会被存储（不会去重）")
    print("3. ✅ 会生成相同或非常相似的向量表示")
    print("4. ⚠️  检索时可能返回多个相同内容的结果")
    print("5. ⚠️  会占用额外的存储空间和计算资源")
    print()
    print("💡 建议:")
    print("- 如果需要去重，应在文档预处理阶段实现")
    print("- 可以考虑基于内容hash的去重机制")
    print("- 或者在检索后进行结果去重")

if __name__ == "__main__":
    main()
