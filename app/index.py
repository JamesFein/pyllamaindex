import logging
import os
from typing import Optional

from llama_index.core.indices import VectorStoreIndex
from llama_index.server.api.models import ChatRequest
from app.storage_config import load_storage_context

logger = logging.getLogger("uvicorn")

STORAGE_DIR = "storage"


def get_index(chat_request: Optional[ChatRequest] = None):
    # check if storage already exists
    if not os.path.exists(STORAGE_DIR):
        return None

    # load the existing storage context with SQLite and ChromaDB
    logger.info(f"Loading index from {STORAGE_DIR} using SQLite and ChromaDB...")
    storage_context = load_storage_context(STORAGE_DIR)

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
        return None
