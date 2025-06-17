#!/usr/bin/env python3
"""
改进的索引生成脚本 - 解决 chunk_index 和重复数据问题
"""
import logging
import os
import hashlib
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def generate_index_improved():
    """
    改进的索引生成函数，解决 chunk_index 和重复数据问题
    """
    from app.index import STORAGE_DIR
    from app.settings import init_settings
    from app.storage_config import get_storage_context
    from llama_index.core.indices import VectorStoreIndex
    from llama_index.core.readers import SimpleDirectoryReader
    from llama_index.core.node_parser import SentenceSplitter

    load_dotenv()
    init_settings()

    logger.info("🔄 开始改进的索引生成（解决 chunk_index 问题）")

    # 1. 检查是否已有数据
    storage_context = get_storage_context(STORAGE_DIR)
    
    # 检查现有文档数量
    try:
        existing_docs = storage_context.docstore.get_all_documents()
        if existing_docs:
            logger.warning(f"⚠️  发现 {len(existing_docs)} 个现有文档")
            logger.warning("建议先运行 reset_data_complete.py 清理数据")
            
            user_input = input("是否继续？这可能导致重复数据 (y/N): ")
            if user_input.lower() != 'y':
                logger.info("❌ 用户取消操作")
                return
    except:
        logger.info("✅ 没有现有数据，继续生成")

    # 2. 读取文档
    data_dir = os.environ.get("DATA_DIR", "data")
    reader = SimpleDirectoryReader(data_dir, recursive=True)
    documents = reader.load_data()
    
    logger.info(f"📄 读取到 {len(documents)} 个文档")
    
    if not documents:
        logger.error("❌ 没有找到文档，请检查 data 目录")
        return

    # 3. 配置分块器（更细粒度的分块）
    parser = SentenceSplitter(
        chunk_size=512,      # 较小的块大小
        chunk_overlap=50,    # 块之间的重叠
        separator=" "        # 按空格分割
    )
    
    # 4. 处理每个文档
    all_processed_nodes = []
    
    for document in documents:
        file_path = document.metadata.get('file_path', '')
        file_name = document.metadata.get('file_name', os.path.basename(file_path))
        
        logger.info(f"📝 处理文档: {file_name}")
        
        # 生成文件ID（基于文件名的哈希）
        file_id = f"file_{hashlib.md5(file_name.encode()).hexdigest()[:8]}"
        
        # 获取文件信息
        try:
            file_stats = os.stat(file_path) if file_path and os.path.exists(file_path) else None
            file_size = file_stats.st_size if file_stats else len(document.text.encode('utf-8'))
        except:
            file_size = len(document.text.encode('utf-8'))
        
        file_type = "text/plain"
        
        # 添加文件记录
        storage_context.docstore.add_file_record(
            file_id=file_id,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            file_hash=""
        )
        
        # 对单个文档进行分块
        doc_nodes = parser.get_nodes_from_documents([document])
        
        logger.info(f"  📊 文档 {file_name} 分成 {len(doc_nodes)} 个块")
        
        # 为每个块添加正确的元数据和 chunk_index
        for chunk_index, node in enumerate(doc_nodes):
            if not hasattr(node, 'metadata'):
                node.metadata = {}
            
            # 添加完整的元数据
            node.metadata.update({
                'file_id': file_id,
                'file_name': file_name,
                'file_size': file_size,
                'file_type': file_type,
                'chunk_index': chunk_index,  # 正确的块索引
                'total_chunks': len(doc_nodes),  # 总块数
                'chunk_size': len(node.text)     # 当前块大小
            })
            
            logger.debug(f"    块 {chunk_index}: {len(node.text)} 字符")
            all_processed_nodes.append(node)
    
    logger.info(f"🧩 总共处理了 {len(all_processed_nodes)} 个文档块")
    
    # 5. 验证 chunk_index 的正确性
    logger.info("🔍 验证 chunk_index 分配...")
    file_chunks = {}
    for node in all_processed_nodes:
        file_name = node.metadata.get('file_name', 'Unknown')
        chunk_index = node.metadata.get('chunk_index', -1)
        
        if file_name not in file_chunks:
            file_chunks[file_name] = []
        file_chunks[file_name].append(chunk_index)
    
    for file_name, chunks in file_chunks.items():
        chunks.sort()
        expected = list(range(len(chunks)))
        if chunks == expected:
            logger.info(f"  ✅ {file_name}: chunk_index 正确 {chunks}")
        else:
            logger.error(f"  ❌ {file_name}: chunk_index 错误 {chunks}, 期望 {expected}")
    
    # 6. 添加到文档存储
    storage_context.docstore.add_documents(all_processed_nodes)
    
    # 7. 创建向量索引
    logger.info("🧠 创建向量索引...")
    index = VectorStoreIndex(
        all_processed_nodes,
        storage_context=storage_context,
        show_progress=True,
    )
    
    # 8. 持久化存储
    storage_context.persist(STORAGE_DIR)
    
    logger.info("🎉 改进的索引生成完成！")
    logger.info(f"📊 统计:")
    logger.info(f"  - 处理文档数: {len(documents)}")
    logger.info(f"  - 生成块数: {len(all_processed_nodes)}")
    logger.info(f"  - 存储位置: {STORAGE_DIR}")
    
    # 9. 最终验证
    logger.info("🔍 最终验证...")
    verify_chunk_index_in_db()

def verify_chunk_index_in_db():
    """验证数据库中的 chunk_index"""
    import sqlite3
    
    try:
        with sqlite3.connect('storage/docstore.db') as conn:
            cursor = conn.execute('''
                SELECT file_name, chunk_index, COUNT(*) as count
                FROM documents 
                GROUP BY file_name, chunk_index 
                ORDER BY file_name, chunk_index
            ''')
            
            logger.info("📊 数据库中的 chunk_index 分布:")
            current_file = None
            for row in cursor.fetchall():
                file_name, chunk_index, count = row
                if file_name != current_file:
                    logger.info(f"  📄 {file_name}:")
                    current_file = file_name
                logger.info(f"    块 {chunk_index}: {count} 个记录")
                
                if count > 1:
                    logger.warning(f"    ⚠️  块 {chunk_index} 有重复记录！")
    except Exception as e:
        logger.error(f"❌ 验证失败: {e}")

if __name__ == "__main__":
    generate_index_improved()
