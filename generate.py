import logging
import os

from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def clear_all_storage_data(storage_context):
    """清理所有存储数据"""
    logger.info("🧹 清理所有存储数据...")
    
    try:
        # 1. 清理 docstore 数据
        import sqlite3
        docstore_path = storage_context.docstore.db_path
        with sqlite3.connect(docstore_path) as conn:
            conn.execute("DELETE FROM documents")
            conn.execute("DELETE FROM files") 
            conn.execute("DELETE FROM ref_doc_info")
            conn.commit()
        logger.info("✅ 清理 docstore 数据完成")
        
        # 2. 清理 index_store 数据
        index_store_path = storage_context.index_store.db_path
        with sqlite3.connect(index_store_path) as conn:
            conn.execute("DELETE FROM index_structs")
            conn.commit()
        logger.info("✅ 清理 index_store 数据完成")
        
        # 3. 清理 chroma 数据并重新创建集合
        try:
            # 获取 ChromaDB 客户端
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            chroma_db_path = os.path.join("storage", "chroma_db_new")
            client = chromadb.PersistentClient(
                path=chroma_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 删除现有集合
            collection_name = "document_vectors"
            try:
                client.delete_collection(collection_name)
                logger.info(f"✅ 删除旧的 ChromaDB 集合: {collection_name}")
            except:
                logger.info("⚠️  旧集合不存在，跳过删除")
            
            # 重新创建集合
            collection = client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"✅ 重新创建 ChromaDB 集合: {collection_name}")
            
        except Exception as e:
            logger.warning(f"⚠️  处理 ChromaDB 时出现问题: {e}")
            
    except Exception as e:
        logger.error(f"❌ 清理数据时出错: {e}")
        raise


def generate_index():
    """
    重新生成索引：清理所有数据，然后重新索引文档
    """
    from app.index import STORAGE_DIR
    from app.settings import init_settings
    from app.storage_config import get_storage_context
    from llama_index.core.indices import VectorStoreIndex
    from llama_index.core.readers import SimpleDirectoryReader
    from llama_index.core.node_parser import SentenceSplitter
    import hashlib

    load_dotenv()
    init_settings()

    logger.info("🚀 开始重新生成索引...")

    # 1. 创建存储上下文
    storage_context = get_storage_context(STORAGE_DIR)

    # 2. 清理所有现有数据
    clear_all_storage_data(storage_context)

    # 3. 重新创建存储上下文（因为 ChromaDB 集合已被重新创建）
    storage_context = get_storage_context(STORAGE_DIR)

    # 4. 读取文档
    data_dir = os.environ.get("DATA_DIR", "data")
    reader = SimpleDirectoryReader(data_dir, recursive=True)
    documents = reader.load_data()
    
    if not documents:
        logger.error("❌ 没有找到文档，请检查 data 目录")
        return

    logger.info(f"📄 读取到 {len(documents)} 个文档")

    # 5. 配置分块器
    parser = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separator=" "
    )
    nodes = parser.get_nodes_from_documents(documents)
    logger.info(f"🧩 分成 {len(nodes)} 个文本块")

    # 6. 处理每个文档，添加文件元数据
    processed_nodes = []
    
    for document in documents:
        file_path = document.metadata.get('file_path', '')
        file_name = document.metadata.get('file_name', os.path.basename(file_path))
        
        logger.info(f"📝 处理文档: {file_name}")
        
        # 生成文件ID（与上传逻辑保持一致）
        file_id = f"file_{hashlib.md5(file_name.encode()).hexdigest()[:8]}"
        
        # 获取文件信息
        try:
            file_stats = os.stat(file_path) if file_path and os.path.exists(file_path) else None
            file_size = file_stats.st_size if file_stats else len(document.text.encode('utf-8'))
        except:
            file_size = len(document.text.encode('utf-8'))
        
        file_type = "text/plain"
        
        # 添加文件记录到 files 表
        storage_context.docstore.add_file_record(
            file_id=file_id,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            file_hash=""
        )
        
        # 找到属于这个文档的所有节点
        doc_nodes = [node for node in nodes if node.ref_doc_id == document.doc_id]
        logger.info(f"  📊 文档 {file_name} 分成 {len(doc_nodes)} 个块")
        
        # 🔧 修复：为每个节点添加正确的元数据，chunk_index 对每个文件从 0 开始
        for chunk_index, node in enumerate(doc_nodes):
            if not hasattr(node, 'metadata'):
                node.metadata = {}
            
            node.metadata.update({
                'file_id': file_id,
                'file_name': file_name,
                'file_size': file_size,
                'file_type': file_type,
                'file_path': file_path,
                'chunk_index': chunk_index  # 🔧 修复：对每个文件从 0 开始
            })
            
            logger.debug(f"    块 {chunk_index}: {len(node.text)} 字符")
            processed_nodes.append(node)

    logger.info(f"✅ 处理完成，共 {len(processed_nodes)} 个文本块")

    # 7. 添加到文档存储
    logger.info("💾 保存到 docstore...")
    storage_context.docstore.add_documents(processed_nodes)

    # 8. 创建向量索引
    logger.info("🧠 创建向量索引...")
    VectorStoreIndex(
        processed_nodes,
        storage_context=storage_context,
        show_progress=True,
    )

    # 9. 持久化存储
    storage_context.persist(STORAGE_DIR)
    
    logger.info("🎉 索引生成完成！")
    logger.info(f"📊 统计:")
    logger.info(f"  - 处理文档数: {len(documents)}")
    logger.info(f"  - 生成块数: {len(processed_nodes)}")
    logger.info(f"  - 存储位置: {STORAGE_DIR}")


def generate_ui_for_workflow():
    """
    Generate UI for UIEventData event in app/workflow.py
    """
    import asyncio

    from main import COMPONENT_DIR

    # To generate UI components for additional event types,
    # import the corresponding data model (e.g., MyCustomEventData)
    # and run the generate_ui_for_workflow function with the imported model.
    # Make sure the output filename of the generated UI component matches the event type (here `ui_event`)
    try:
        from app.workflow import UIEventData  # type: ignore
    except ImportError:
        raise ImportError("Couldn't generate UI component for the current workflow.")
    from llama_index.server.gen_ui import generate_event_component

    # works also well with Claude 3.7 Sonnet or Gemini Pro 2.5
    llm = OpenAI(model="gpt-4.1")
    code = asyncio.run(generate_event_component(event_cls=UIEventData, llm=llm))
    with open(f"{COMPONENT_DIR}/ui_event.jsx", "w") as f:
        f.write(code)
