#!/usr/bin/env python3
"""
Script to update existing documents with file metadata from the data directory.
"""

import sqlite3
import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_file_metadata():
    """Update existing documents with file metadata."""
    db_path = "storage/docstore.db"
    data_dir = "data"
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return False
    
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return False
    
    try:
        # Get all files in data directory
        data_files = {}
        for file_path in Path(data_dir).rglob("*"):
            if file_path.is_file():
                file_name = file_path.name
                file_size = file_path.stat().st_size
                file_type = "application/pdf" if file_name.endswith('.pdf') else "text/plain"
                data_files[file_name] = {
                    'file_name': file_name,
                    'file_size': file_size,
                    'file_type': file_type,
                    'file_path': str(file_path)
                }
        
        logger.info(f"Found {len(data_files)} files in data directory")
        
        with sqlite3.connect(db_path) as conn:
            # Get all documents
            cursor = conn.execute("SELECT doc_id, data FROM documents WHERE file_name IS NULL")
            documents = cursor.fetchall()
            
            logger.info(f"Found {len(documents)} documents without metadata")
            
            updated_count = 0
            for doc_id, doc_data in documents:
                try:
                    # Parse document data to get metadata
                    doc_dict = json.loads(doc_data)
                    
                    # Try to find matching file by looking at metadata
                    file_name = None
                    if 'metadata' in doc_dict and doc_dict['metadata']:
                        metadata = doc_dict['metadata']
                        if 'file_name' in metadata:
                            file_name = metadata['file_name']
                        elif 'file_path' in metadata:
                            file_name = os.path.basename(metadata['file_path'])
                    
                    # If no file name found, try to match by content or other means
                    if not file_name:
                        # For now, skip documents without clear file association
                        continue
                    
                    # Find matching file in data directory
                    if file_name in data_files:
                        file_info = data_files[file_name]
                        
                        # Update database
                        conn.execute("""
                            UPDATE documents 
                            SET file_name = ?, file_size = ?, file_type = ?, upload_date = created_at
                            WHERE doc_id = ?
                        """, (file_info['file_name'], file_info['file_size'], file_info['file_type'], doc_id))
                        
                        updated_count += 1
                        logger.info(f"Updated document {doc_id} with file {file_name}")
                    
                except Exception as e:
                    logger.warning(f"Error processing document {doc_id}: {e}")
                    continue
            
            # For documents that we couldn't match, let's try a different approach
            # Update all remaining documents with generic metadata based on their content
            cursor = conn.execute("SELECT doc_id FROM documents WHERE file_name IS NULL")
            remaining_docs = cursor.fetchall()
            
            for (doc_id,) in remaining_docs:
                # Set generic metadata
                conn.execute("""
                    UPDATE documents 
                    SET file_name = ?, file_size = 0, file_type = 'text/plain', upload_date = created_at
                    WHERE doc_id = ?
                """, (f"document_{doc_id[:8]}.txt", doc_id))
                updated_count += 1
            
            conn.commit()
            logger.info(f"Updated {updated_count} documents with file metadata")
            return True
            
    except Exception as e:
        logger.error(f"Update failed: {e}")
        return False

if __name__ == "__main__":
    update_file_metadata()
