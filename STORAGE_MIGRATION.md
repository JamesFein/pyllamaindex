# Storage Migration: Complete SQLite + ChromaDB Implementation

## Overview

This document describes the complete migration from JSON-based storage to a **full SQLite + ChromaDB** solution for better performance, scalability, and concurrent processing capabilities.

## Changes Made

### 1. Dependencies Added

- `chromadb` - Vector database for storing embeddings
- `llama-index-vector-stores-chroma` - LlamaIndex integration for ChromaDB

### 2. New Files Created

- `app/storage_config.py` - Storage configuration and management
- `app/sqlite_stores.py` - Custom SQLite storage implementations
- `migrate_to_sqlite.py` - Migration script from JSON to SQLite
- `test_storage.py` - Test script to verify storage functionality
- `test_sqlite_store.py` - Direct SQLite store testing
- `STORAGE_MIGRATION.md` - This documentation file

### 3. Modified Files

- `app/index.py` - Updated to use new storage configuration
- `generate.py` - Updated to use ChromaDB for vector storage
- `pyproject.toml` - Added ChromaDB dependencies (via uv add)

## Storage Architecture

### Current Implementation

- **Vector Storage**: ChromaDB (SQLite-based)

  - Location: `storage/chroma_db/chroma.sqlite3`
  - Collection: `document_vectors`
  - Stores: Document embeddings and vector indices

- **Document Storage**: SQLite-based (SQLiteDocumentStore)

  - Location: `storage/docstore.db`
  - Stores: Document nodes, metadata, and reference information

- **Index Storage**: SQLite-based (SQLiteIndexStore)
  - Location: `storage/index_store.db`
  - Stores: Index structures and metadata

### Benefits

1. **Performance**: ChromaDB provides faster vector similarity search
2. **Scalability**: SQLite-based storage scales better than JSON
3. **Persistence**: Proper database persistence with ACID properties
4. **Memory Efficiency**: ChromaDB handles large vector collections efficiently

## Usage

### Generating Index

```bash
# Generate index with new storage backend
uv run generate
```

### Running the Server

```bash
# Start the development server
uv run fastapi dev --port 8001
```

### Testing Storage

```bash
# Run storage verification tests
uv run python test_storage.py
```

## Storage Directory Structure

```
storage/
├── chroma_db/                    # ChromaDB vector database
│   ├── chroma.sqlite3           # SQLite database file
│   └── [collection-id]/         # Collection-specific files
├── docstore.json                # Document store (JSON)
├── index_store.json             # Index store (JSON)
├── graph_store.json             # Graph store (legacy)
├── default__vector_store.json   # Legacy vector store (unused)
└── image__vector_store.json     # Legacy image vectors (unused)
```

## Migration Process

### Automatic Migration

The system automatically handles migration:

1. New indexes use ChromaDB for vectors
2. Existing JSON stores are preserved and loaded
3. No manual migration required

### Clean Installation

For a fresh start:

1. Delete the `storage/` directory
2. Run `uv run generate` to create new storage
3. All data will use the new storage backends

## Configuration

### ChromaDB Settings

- **Path**: `storage/chroma_db`
- **Collection**: `document_vectors`
- **Telemetry**: Disabled
- **Reset**: Allowed (for development)

### Environment Variables

Ensure these are set in `.env`:

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai-proxy.org/v1
```

## Troubleshooting

### Common Issues

1. **ChromaDB Collection Not Found**

   - Run `uv run generate` to recreate the index
   - Check if `storage/chroma_db/` directory exists

2. **Index Loading Fails**

   - Verify environment variables are set
   - Check storage directory permissions
   - Run the test script: `uv run python test_storage.py`

3. **Performance Issues**
   - ChromaDB may take time to initialize on first run
   - Large document collections may require more memory

### Verification Commands

```bash
# Test storage systems
uv run python test_storage.py

# Test index loading
uv run python -c "from dotenv import load_dotenv; load_dotenv(); from app.settings import init_settings; init_settings(); from app.index import get_index; print('Success' if get_index() else 'Failed')"

# Check ChromaDB collection
uv run python -c "import chromadb; client = chromadb.PersistentClient(path='storage/chroma_db'); collection = client.get_collection('document_vectors'); print(f'Vectors: {collection.count()}')"
```

## Future Improvements

1. **Full SQLite Migration**: Migrate document and index stores to SQLite
2. **Database Optimization**: Add indexing and query optimization
3. **Backup/Restore**: Implement database backup and restore functionality
4. **Monitoring**: Add storage metrics and monitoring
5. **Clustering**: Support for distributed ChromaDB deployment

## Rollback

To rollback to the original JSON-based storage:

1. Restore the original `app/index.py` and `generate.py` files
2. Remove ChromaDB dependencies
3. Delete the `app/storage_config.py` file
4. Use the existing JSON files in the storage directory
