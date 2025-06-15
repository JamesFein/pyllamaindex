#!/usr/bin/env python3
"""
Migration script to convert JSON storage to SQLite storage.
"""

import os
import logging
import shutil
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main migration function."""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize settings
    from app.settings import init_settings
    init_settings()
    
    storage_dir = "storage"
    
    logger.info("=== SQLite Migration Script ===")
    logger.info(f"Storage directory: {storage_dir}")
    
    # Check if storage directory exists
    if not os.path.exists(storage_dir):
        logger.error(f"Storage directory {storage_dir} does not exist!")
        return False
    
    # Check if JSON files exist
    json_files = {
        "docstore.json": os.path.join(storage_dir, "docstore.json"),
        "index_store.json": os.path.join(storage_dir, "index_store.json")
    }
    
    existing_json_files = {name: path for name, path in json_files.items() if os.path.exists(path)}
    
    if not existing_json_files:
        logger.info("No JSON files found to migrate. System may already be using SQLite.")
        return True
    
    logger.info(f"Found JSON files to migrate: {list(existing_json_files.keys())}")
    
    # Check if SQLite files already exist
    sqlite_files = {
        "docstore.db": os.path.join(storage_dir, "docstore.db"),
        "index_store.db": os.path.join(storage_dir, "index_store.db")
    }
    
    existing_sqlite_files = {name: path for name, path in sqlite_files.items() if os.path.exists(path)}
    
    if existing_sqlite_files:
        logger.warning(f"SQLite files already exist: {list(existing_sqlite_files.keys())}")
        response = input("Do you want to overwrite existing SQLite files? (y/N): ")
        if response.lower() != 'y':
            logger.info("Migration cancelled by user.")
            return False
        
        # Backup existing SQLite files
        backup_dir = os.path.join(storage_dir, "backup_sqlite")
        os.makedirs(backup_dir, exist_ok=True)
        
        for name, path in existing_sqlite_files.items():
            backup_path = os.path.join(backup_dir, name)
            shutil.copy2(path, backup_path)
            logger.info(f"Backed up {name} to {backup_path}")
    
    # Perform migration
    logger.info("Starting migration process...")
    
    try:
        from app.storage_config import migrate_json_to_sqlite
        
        success = migrate_json_to_sqlite(storage_dir)
        
        if success:
            logger.info("✅ Migration completed successfully!")
            
            # Create backup of JSON files
            backup_dir = os.path.join(storage_dir, "backup_json")
            os.makedirs(backup_dir, exist_ok=True)
            
            for name, path in existing_json_files.items():
                backup_path = os.path.join(backup_dir, name)
                shutil.copy2(path, backup_path)
                logger.info(f"Backed up {name} to {backup_path}")
            
            # Ask if user wants to delete JSON files
            response = input("Migration successful! Do you want to delete the original JSON files? (y/N): ")
            if response.lower() == 'y':
                for name, path in existing_json_files.items():
                    os.remove(path)
                    logger.info(f"Deleted {name}")
                logger.info("Original JSON files deleted. Backups are available in backup_json/")
            else:
                logger.info("Original JSON files preserved.")
            
            # Test the new storage
            logger.info("Testing new SQLite storage...")
            test_storage()
            
            return True
        else:
            logger.error("❌ Migration failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed with error: {e}")
        return False


def test_storage():
    """Test the new SQLite storage."""
    try:
        from app.storage_config import load_storage_context
        
        storage_context = load_storage_context("storage")
        if storage_context:
            logger.info("✅ SQLite storage context loaded successfully")
            
            # Test document store
            doc_count = len(storage_context.docstore.docs)
            logger.info(f"✅ Document store: {doc_count} documents")
            
            # Test index store
            index_count = len(storage_context.index_store.index_structs)
            logger.info(f"✅ Index store: {index_count} index structures")
            
            # Test loading index
            from app.index import get_index
            index = get_index()
            if index:
                logger.info("✅ Index loaded successfully with SQLite storage")
            else:
                logger.warning("⚠️ Could not load index (this may be normal if no index exists)")
                
        else:
            logger.error("❌ Could not load SQLite storage context")
            
    except Exception as e:
        logger.error(f"❌ Storage test failed: {e}")


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Migration completed successfully!")
        print("Your system is now using SQLite for document and index storage.")
        print("ChromaDB is being used for vector storage.")
        print("\nNext steps:")
        print("1. Test your application to ensure everything works correctly")
        print("2. If everything works, you can delete the backup_json/ directory")
        print("3. Run 'uv run python test_storage.py' to verify the storage")
    else:
        print("\n❌ Migration failed. Please check the logs above.")
        print("Your original JSON files are preserved.")
