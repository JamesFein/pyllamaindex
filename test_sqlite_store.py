#!/usr/bin/env python3
"""
Test script to verify SQLite document store functionality.
"""

import os
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sqlite_docstore():
    """Test SQLite document store directly."""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize settings
    from app.settings import init_settings
    init_settings()
    
    from app.sqlite_stores import SQLiteDocumentStore
    from llama_index.core.schema import TextNode
    
    logger.info("=== Testing SQLite Document Store ===")
    
    # Create test document store
    test_db_path = "test_docstore.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    docstore = SQLiteDocumentStore(test_db_path)
    
    # Create test nodes
    test_nodes = [
        TextNode(text="This is test document 1", node_id="test_1"),
        TextNode(text="This is test document 2", node_id="test_2"),
        TextNode(text="This is test document 3", node_id="test_3"),
    ]

    # Test adding documents
    logger.info("Testing add_documents...")
    docstore.add_documents(test_nodes)

    # Test retrieving documents
    logger.info("Testing document retrieval...")
    docs = docstore.docs
    logger.info(f"Retrieved {len(docs)} documents")

    actual_doc_ids = list(docs.keys())
    for doc_id, doc in docs.items():
        logger.info(f"  - {doc_id}: {doc.text[:50]}...")

    # Test individual document retrieval using actual ID
    logger.info("Testing individual document retrieval...")
    if actual_doc_ids:
        first_doc_id = actual_doc_ids[0]
        doc1 = docstore.get_document(first_doc_id)
        logger.info(f"Retrieved doc {first_doc_id}: {doc1.text}")

        # Test document existence
        logger.info("Testing document existence...")
        exists = docstore.document_exists(first_doc_id)
        logger.info(f"Document {first_doc_id} exists: {exists}")
    else:
        logger.error("No documents found!")
    
    # Clean up
    try:
        os.remove(test_db_path)
    except PermissionError:
        logger.warning(f"Could not delete {test_db_path} - file may be in use")
    logger.info("✅ SQLite document store test completed successfully!")


def test_index_creation_with_debug():
    """Test index creation with debug logging to see what's happening."""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize settings
    from app.settings import init_settings
    init_settings()
    
    logger.info("=== Testing Index Creation with Debug ===")
    
    from llama_index.core.readers import SimpleDirectoryReader
    from llama_index.core.indices import VectorStoreIndex
    from app.storage_config import get_storage_context
    
    # Create storage context
    storage_context = get_storage_context("test_storage")
    
    # Load documents
    reader = SimpleDirectoryReader("data", recursive=True)
    documents = reader.load_data()
    logger.info(f"Loaded {len(documents)} documents")
    
    # Create index
    logger.info("Creating index...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )
    
    # Check what was stored
    logger.info("Checking storage after index creation...")
    logger.info(f"Docstore docs count: {len(storage_context.docstore.docs)}")
    logger.info(f"Index store count: {len(storage_context.index_store.index_structs)}")
    
    # Persist
    storage_context.persist("test_storage")
    
    # Clean up
    import shutil
    if os.path.exists("test_storage"):
        shutil.rmtree("test_storage")
    
    logger.info("✅ Index creation test completed!")


if __name__ == "__main__":
    test_sqlite_docstore()
    test_index_creation_with_debug()
