import logging
import os
from typing import Optional

from llama_index.core.indices import VectorStoreIndex
from llama_index.server.api.models import ChatRequest
from app.storage_config import load_storage_context

logger = logging.getLogger("uvicorn")

STORAGE_DIR = "storage"


def get_index(chat_request: Optional[ChatRequest] = None):
    # 🔧 添加详细调试信息
    current_dir = os.getcwd()
    logger.info(f"🔍 get_index called from directory: {current_dir}")
    logger.info(f"🔍 STORAGE_DIR: {STORAGE_DIR}")
    logger.info(f"🔍 Full storage path: {os.path.abspath(STORAGE_DIR)}")

    # check if storage already exists
    if not os.path.exists(STORAGE_DIR):
        logger.error(f"❌ Storage directory does not exist: {os.path.abspath(STORAGE_DIR)}")
        return None

    # 检查存储目录内容
    try:
        storage_files = os.listdir(STORAGE_DIR)
        logger.info(f"📁 Storage directory contents: {storage_files}")
    except Exception as e:
        logger.error(f"❌ Cannot list storage directory: {e}")
        return None

    # load the existing storage context with SQLite and ChromaDB
    logger.info(f"Loading index from {STORAGE_DIR} using SQLite and ChromaDB...")

    try:
        storage_context = load_storage_context(STORAGE_DIR)
    except Exception as e:
        logger.error(f"❌ Exception loading storage context: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None

    if storage_context is None:
        logger.warning(f"Could not load storage context from {STORAGE_DIR}")
        return None

    try:
        # Load VectorStoreIndex from vector store directly
        # This is the correct approach for VectorStoreIndex with custom storage
        index = VectorStoreIndex.from_vector_store(
            storage_context.vector_store,
            storage_context=storage_context
        )
        logger.info(f"Successfully loaded index from {STORAGE_DIR}")
        return index
    except Exception as e:
        logger.error(f"Failed to load index from storage: {e}")
        import traceback
        logger.error(f"❌ Index creation traceback: {traceback.format_exc()}")
        return None
