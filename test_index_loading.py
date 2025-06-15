#!/usr/bin/env python3
"""Test script to verify index loading works correctly."""

import logging
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_index_loading():
    """Test loading the index from storage."""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize settings
    from app.settings import init_settings
    init_settings()
    
    logger.info("=== Testing Index Loading ===")
    
    # Test the get_index function
    from app.index import get_index
    
    try:
        logger.info("Attempting to load index...")
        index = get_index()
        
        if index is None:
            logger.error("❌ Index loading returned None")
            return False
        
        logger.info("✅ Index loaded successfully!")
        
        # Test a simple query
        logger.info("Testing query engine...")
        query_engine = index.as_query_engine()
        response = query_engine.query("What are the main topics in the documents?")
        
        logger.info(f"✅ Query successful! Response: {response.response[:100]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ Index loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_index_loading()
    if success:
        logger.info("🎉 Index loading test PASSED!")
    else:
        logger.error("💥 Index loading test FAILED!")
        exit(1)
