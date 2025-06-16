#!/usr/bin/env python3
"""
Database migration script to add file metadata columns to existing documents table.
"""

import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migrate the database to add new columns."""
    db_path = "storage/docstore.db"
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Check current schema
            cursor = conn.execute("PRAGMA table_info(documents)")
            columns = [row[1] for row in cursor.fetchall()]
            logger.info(f"Current columns: {columns}")
            
            # Add missing columns
            new_columns = [
                ("file_name", "TEXT"),
                ("file_size", "INTEGER"),
                ("file_type", "TEXT"),
                ("upload_date", "TIMESTAMP")
            ]
            
            for column_name, column_type in new_columns:
                if column_name not in columns:
                    try:
                        conn.execute(f"ALTER TABLE documents ADD COLUMN {column_name} {column_type}")
                        logger.info(f"Added column: {column_name}")
                    except sqlite3.Error as e:
                        logger.error(f"Error adding column {column_name}: {e}")
            
            # Create index if it doesn't exist
            try:
                conn.execute("CREATE INDEX IF NOT EXISTS idx_upload_date ON documents(upload_date DESC)")
                logger.info("Created upload_date index")
            except sqlite3.Error as e:
                logger.error(f"Error creating index: {e}")
            
            # Update existing records with default values
            conn.execute("""
                UPDATE documents 
                SET upload_date = created_at 
                WHERE upload_date IS NULL
            """)
            
            conn.commit()
            logger.info("Database migration completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    migrate_database()
