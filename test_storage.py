#!/usr/bin/env python3
"""
Test script to verify SQLite and ChromaDB storage implementation.
"""

import os
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_storage_systems():
    """Test both ChromaDB and SQLite storage systems."""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize settings
    from app.settings import init_settings
    init_settings()
    
    logger.info("=== Testing Storage Systems ===")
    
    # Test 1: Check if ChromaDB is working
    logger.info("1. Testing ChromaDB vector store...")
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        chroma_client = chromadb.PersistentClient(
            path="storage/chroma_db",
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Try to get the specific collection we use
        try:
            collection = chroma_client.get_collection("document_vectors")
            count = collection.count()
            logger.info(f"   Collection 'document_vectors' has {count} vectors")
        except Exception as e:
            logger.info(f"   Collection 'document_vectors' not found or empty: {e}")
        
        logger.info("   ✅ ChromaDB is working correctly")
        
    except Exception as e:
        logger.error(f"   ❌ ChromaDB test failed: {e}")
    
    # Test 2: Check if document store is working
    logger.info("2. Testing document store...")
    try:
        from app.storage_config import load_storage_context
        
        storage_context = load_storage_context("storage")
        if storage_context:
            docstore = storage_context.docstore
            doc_count = len(docstore.docs)
            logger.info(f"   Document store has {doc_count} documents")
            logger.info("   ✅ Document store is working correctly")
        else:
            logger.error("   ❌ Could not load storage context")
            
    except Exception as e:
        logger.error(f"   ❌ Document store test failed: {e}")
    
    # Test 3: Check if we can create a new index from existing storage
    logger.info("3. Testing index creation from existing storage...")
    try:
        from app.storage_config import load_storage_context
        from llama_index.core.indices import VectorStoreIndex

        storage_context = load_storage_context("storage")
        if storage_context:
            # Create index from existing vector store
            index = VectorStoreIndex.from_vector_store(
                storage_context.vector_store,
                storage_context=storage_context
            )
            logger.info("   ✅ Index created from existing storage")

            # Test a simple query
            query_engine = index.as_query_engine()
            response = query_engine.query("What are the dimensional standards for letters?")
            logger.info(f"   Sample query response: {response.response[:100]}...")
            logger.info("   ✅ Query engine is working correctly")
        else:
            logger.error("   ❌ Could not load storage context")

    except Exception as e:
        logger.error(f"   ❌ Index creation test failed: {e}")
    
    # Test 4: Check storage files
    logger.info("4. Checking storage files...")
    storage_files = {
        "ChromaDB": "storage/chroma_db/chroma.sqlite3",
        "SQLite Document Store": "storage/docstore.db",
        "SQLite Index Store": "storage/index_store.db"
    }

    for name, path in storage_files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            logger.info(f"   ✅ {name}: {path} ({size} bytes)")
        else:
            logger.error(f"   ❌ {name}: {path} not found")
    
    logger.info("=== Storage Test Complete ===")

if __name__ == "__main__":
    test_storage_systems()
