import os
import logging
from typing import Optional
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.sqlite_stores import SQLiteDocumentStore, SQLiteIndexStore

logger = logging.getLogger(__name__)

def get_storage_context(storage_dir: str = "storage") -> StorageContext:
    """
    Create a storage context using SQLite for docstore/index store and ChromaDB for vector store.
    
    Args:
        storage_dir: Directory to store the databases
        
    Returns:
        StorageContext configured with SQLite and ChromaDB backends
    """
    # Ensure storage directory exists
    os.makedirs(storage_dir, exist_ok=True)
    
    # Configure ChromaDB client
    chroma_db_path = os.path.join(storage_dir, "chroma_db")
    chroma_client = chromadb.PersistentClient(
        path=chroma_db_path,
        settings=ChromaSettings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    # Get or create collection for vector storage
    collection_name = "document_vectors"
    try:
        chroma_collection = chroma_client.get_collection(collection_name)
        logger.info(f"Using existing ChromaDB collection: {collection_name}")
    except Exception:
        chroma_collection = chroma_client.create_collection(collection_name)
        logger.info(f"Created new ChromaDB collection: {collection_name}")
    
    # Create ChromaDB vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Configure SQLite-based document store
    docstore_path = os.path.join(storage_dir, "docstore.db")
    docstore = SQLiteDocumentStore(docstore_path)

    # Configure SQLite-based index store
    index_store_path = os.path.join(storage_dir, "index_store.db")
    index_store = SQLiteIndexStore(index_store_path)
    
    # Create storage context
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore,
        index_store=index_store
    )
    
    logger.info(f"Storage context created with:")
    logger.info(f"  - ChromaDB vector store: {chroma_db_path}")
    logger.info(f"  - SQLite document store: {docstore_path}")
    logger.info(f"  - SQLite index store: {index_store_path}")
    
    return storage_context


def load_storage_context(storage_dir: str = "storage") -> Optional[StorageContext]:
    """
    Load existing storage context from ChromaDB and SQLite stores.

    Args:
        storage_dir: Directory containing the databases

    Returns:
        StorageContext if databases exist, None otherwise
    """
    # Check if storage directory exists
    if not os.path.exists(storage_dir):
        logger.info(f"Storage directory {storage_dir} does not exist")
        return None

    # Check if ChromaDB directory exists
    chroma_db_path = os.path.join(storage_dir, "chroma_db")
    if not os.path.exists(chroma_db_path):
        logger.info(f"ChromaDB directory {chroma_db_path} does not exist")
        return None

    try:
        # Configure ChromaDB client
        chroma_client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get existing collection
        collection_name = "document_vectors"
        chroma_collection = chroma_client.get_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        # Load SQLite stores
        docstore_path = os.path.join(storage_dir, "docstore.db")
        index_store_path = os.path.join(storage_dir, "index_store.db")

        docstore = SQLiteDocumentStore(docstore_path)
        index_store = SQLiteIndexStore(index_store_path)

        # Create storage context
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            docstore=docstore,
            index_store=index_store
        )

        logger.info(f"Loaded existing storage context from {storage_dir}")
        return storage_context

    except Exception as e:
        logger.error(f"Failed to load storage context: {e}")
        return None


def migrate_json_to_sqlite(storage_dir: str = "storage") -> bool:
    """
    Migrate existing JSON storage to SQLite.

    Args:
        storage_dir: Directory containing the storage files

    Returns:
        True if migration was successful, False otherwise
    """
    import json
    import sqlite3
    from llama_index.core.storage.docstore import SimpleDocumentStore
    from llama_index.core.storage.index_store import SimpleIndexStore

    logger.info("Starting migration from JSON to SQLite...")

    try:
        # Check if JSON files exist
        docstore_json_path = os.path.join(storage_dir, "docstore.json")
        index_store_json_path = os.path.join(storage_dir, "index_store.json")

        # Migrate document store
        if os.path.exists(docstore_json_path):
            logger.info("Migrating document store from JSON to SQLite...")

            # Load from JSON
            json_docstore = SimpleDocumentStore.from_persist_path(docstore_json_path)

            # Create SQLite store
            docstore_db_path = os.path.join(storage_dir, "docstore.db")
            sqlite_docstore = SQLiteDocumentStore(docstore_db_path)

            # Migrate documents
            if json_docstore.docs:
                documents = list(json_docstore.docs.values())
                sqlite_docstore.add_documents(documents)
                logger.info(f"Migrated {len(documents)} documents to SQLite")

            # Migrate ref doc info
            ref_doc_info = json_docstore.get_all_ref_doc_info()
            if ref_doc_info:
                with sqlite3.connect(docstore_db_path) as conn:
                    for ref_doc_id, info in ref_doc_info.items():
                        node_ids_json = json.dumps(info.get("node_ids", []))
                        metadata_json = json.dumps(info.get("metadata", {}))
                        conn.execute("""
                            INSERT OR REPLACE INTO ref_doc_info (ref_doc_id, node_ids, metadata)
                            VALUES (?, ?, ?)
                        """, (ref_doc_id, node_ids_json, metadata_json))
                    conn.commit()
                logger.info(f"Migrated {len(ref_doc_info)} reference documents to SQLite")

        # Migrate index store
        if os.path.exists(index_store_json_path):
            logger.info("Migrating index store from JSON to SQLite...")

            # Load from JSON
            json_index_store = SimpleIndexStore.from_persist_path(index_store_json_path)

            # Create SQLite store
            index_store_db_path = os.path.join(storage_dir, "index_store.db")
            sqlite_index_store = SQLiteIndexStore(index_store_db_path)

            # Migrate index structures
            index_structs = json_index_store.index_structs
            if index_structs:
                # Handle both dict and property cases
                if hasattr(index_structs, 'values'):
                    structs_to_migrate = index_structs.values()
                    count = len(index_structs)
                else:
                    # If it's a property that returns a dict
                    structs_dict = index_structs if isinstance(index_structs, dict) else {}
                    structs_to_migrate = structs_dict.values()
                    count = len(structs_dict)

                for index_struct in structs_to_migrate:
                    sqlite_index_store.add_index_struct(index_struct)
                logger.info(f"Migrated {count} index structures to SQLite")

        logger.info("Migration from JSON to SQLite completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
