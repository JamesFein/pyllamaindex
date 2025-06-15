#!/usr/bin/env python3
"""Test script to verify vector store index loading works correctly."""

import logging
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_vector_store_loading():
    """Test loading the index from vector store directly."""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize settings
    from app.settings import init_settings
    init_settings()
    
    logger.info("=== Testing Vector Store Index Loading ===")
    
    try:
        from app.storage_config import load_storage_context
        from llama_index.core.indices import VectorStoreIndex
        
        # Load storage context
        storage_context = load_storage_context("storage")
        if storage_context is None:
            logger.error("❌ Could not load storage context")
            return False
        
        logger.info("✅ Storage context loaded successfully")
        
        # Try to create index from vector store directly
        logger.info("Creating index from vector store...")
        index = VectorStoreIndex.from_vector_store(
            storage_context.vector_store,
            storage_context=storage_context
        )
        
        logger.info("✅ Index created from vector store successfully!")
        
        # Test a simple query
        logger.info("Testing query engine...")
        query_engine = index.as_query_engine()
        response = query_engine.query("What are the main topics in the documents?")
        
        logger.info(f"✅ Query successful! Response: {response.response[:100]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ Vector store index loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vector_store_loading()
    if success:
        logger.info("🎉 Vector store index loading test PASSED!")
    else:
        logger.error("💥 Vector store index loading test FAILED!")
        exit(1)
