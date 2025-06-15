#!/usr/bin/env python3
"""Debug script to examine the index store database."""

import sqlite3
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_index_store():
    """Debug the index store database."""
    
    db_path = "storage/index_store.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT index_id, data FROM index_structs")
            
            for row in cursor.fetchall():
                index_id, data_json = row
                data = json.loads(data_json)
                
                logger.info(f"Index ID: {index_id}")
                logger.info(f"Data keys: {list(data.keys())}")
                logger.info(f"Class name: {data.get('class_name', 'N/A')}")
                logger.info(f"Index type: {data.get('index_type', 'N/A')}")
                logger.info(f"Data sample: {str(data)[:200]}...")
                logger.info("-" * 50)
                
    except Exception as e:
        logger.error(f"Error reading index store: {e}")

if __name__ == "__main__":
    debug_index_store()
