import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any
from llama_index.core.storage.docstore.types import BaseDocumentStore
from llama_index.core.storage.index_store.types import BaseIndexStore
from llama_index.core.schema import BaseNode, Document, TextNode
from llama_index.core.data_structs.data_structs import IndexStruct

logger = logging.getLogger(__name__)


class SQLiteDocumentStore(BaseDocumentStore):
    """SQLite-based document store for better performance and concurrency."""
    
    def __init__(self, db_path: str):
        """Initialize SQLite document store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        logger.info(f"🔥 Initializing SQLiteDocumentStore at {db_path}")
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    doc_hash TEXT,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS ref_doc_info (
                    ref_doc_id TEXT PRIMARY KEY,
                    node_ids TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_hash ON documents(doc_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_updated_at ON documents(updated_at)")
            conn.commit()

    def _deserialize_node(self, node_data: dict) -> BaseNode:
        """Deserialize node data back to the correct node type."""
        from llama_index.core.schema import TextNode, ImageNode, IndexNode

        # Get the class name from the serialized data
        class_name = node_data.get("class_name", "TextNode")

        # Map class names to actual classes
        node_classes = {
            "TextNode": TextNode,
            "ImageNode": ImageNode,
            "IndexNode": IndexNode,
            "Document": Document,
        }

        # Get the appropriate class, default to TextNode
        node_class = node_classes.get(class_name, TextNode)

        try:
            return node_class.from_dict(node_data)
        except Exception as e:
            logger.warning(f"Failed to deserialize node with class {class_name}, falling back to TextNode: {e}")
            # Fallback to TextNode if deserialization fails
            return TextNode.from_dict(node_data)
    
    def add_documents(self, nodes: List[BaseNode], allow_update: bool = True) -> None:
        """Add documents to the store."""
        logger.info(f"🔥 SQLiteDocumentStore.add_documents called with {len(nodes)} nodes")
        with sqlite3.connect(self.db_path) as conn:
            for node in nodes:
                doc_data = node.to_dict()
                doc_json = json.dumps(doc_data)
                doc_hash = getattr(node, 'hash', None)

                logger.debug(f"Adding node {node.node_id} with hash {doc_hash}")

                if allow_update:
                    conn.execute("""
                        INSERT OR REPLACE INTO documents (doc_id, doc_hash, data, updated_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """, (node.node_id, doc_hash, doc_json))
                else:
                    conn.execute("""
                        INSERT OR IGNORE INTO documents (doc_id, doc_hash, data)
                        VALUES (?, ?, ?)
                    """, (node.node_id, doc_hash, doc_json))
            conn.commit()
        logger.info(f"✅ Successfully added {len(nodes)} documents to SQLite store")
    
    def get_document(self, doc_id: str, raise_error: bool = True) -> Optional[BaseNode]:
        """Get document by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM documents WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()

            if row is None:
                if raise_error:
                    raise ValueError(f"Document {doc_id} not found")
                return None

            doc_data = json.loads(row[0])
            return self._deserialize_node(doc_data)
    
    def get_node(self, node_id: str, raise_error: bool = True) -> Optional[BaseNode]:
        """Get node by ID (alias for get_document)."""
        return self.get_document(node_id, raise_error)
    
    def get_nodes(self, node_ids: List[str], raise_error: bool = True) -> List[BaseNode]:
        """Get multiple nodes by IDs."""
        nodes = []
        for node_id in node_ids:
            node = self.get_node(node_id, raise_error=False)
            if node is not None:
                nodes.append(node)
            elif raise_error:
                raise ValueError(f"Node {node_id} not found")
        return nodes
    
    def delete_document(self, doc_id: str, raise_error: bool = True) -> None:
        """Delete document by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
            if cursor.rowcount == 0 and raise_error:
                raise ValueError(f"Document {doc_id} not found")
            conn.commit()
    
    def document_exists(self, doc_id: str) -> bool:
        """Check if document exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM documents WHERE doc_id = ? LIMIT 1", (doc_id,))
            return cursor.fetchone() is not None
    
    def get_all_document_hashes(self) -> Dict[str, str]:
        """Get all document hashes."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT doc_id, doc_hash FROM documents WHERE doc_hash IS NOT NULL")
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    def get_document_hash(self, doc_id: str) -> Optional[str]:
        """Get document hash by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT doc_hash FROM documents WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def set_document_hash(self, doc_id: str, doc_hash: str) -> None:
        """Set document hash."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE documents SET doc_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE doc_id = ?
            """, (doc_hash, doc_id))
            conn.commit()

    def set_document_hashes(self, doc_hashes: Dict[str, str]) -> None:
        """Set multiple document hashes."""
        with sqlite3.connect(self.db_path) as conn:
            for doc_id, doc_hash in doc_hashes.items():
                conn.execute("""
                    UPDATE documents SET doc_hash = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE doc_id = ?
                """, (doc_hash, doc_id))
            conn.commit()
    
    def get_all_ref_doc_info(self) -> Dict[str, Any]:
        """Get all reference document info."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT ref_doc_id, node_ids, metadata FROM ref_doc_info")
            result = {}
            for row in cursor.fetchall():
                ref_doc_id, node_ids_json, metadata_json = row
                result[ref_doc_id] = {
                    "node_ids": json.loads(node_ids_json),
                    "metadata": json.loads(metadata_json) if metadata_json else {}
                }
            return result
    
    def get_ref_doc_info(self, ref_doc_id: str) -> Optional[Dict[str, Any]]:
        """Get reference document info by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT node_ids, metadata FROM ref_doc_info WHERE ref_doc_id = ?", 
                (ref_doc_id,)
            )
            row = cursor.fetchone()
            if row:
                node_ids_json, metadata_json = row
                return {
                    "node_ids": json.loads(node_ids_json),
                    "metadata": json.loads(metadata_json) if metadata_json else {}
                }
            return None
    
    def delete_ref_doc(self, ref_doc_id: str, raise_error: bool = True) -> None:
        """Delete reference document."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM ref_doc_info WHERE ref_doc_id = ?", (ref_doc_id,))
            if cursor.rowcount == 0 and raise_error:
                raise ValueError(f"Reference document {ref_doc_id} not found")
            conn.commit()
    
    def ref_doc_exists(self, ref_doc_id: str) -> bool:
        """Check if reference document exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM ref_doc_info WHERE ref_doc_id = ? LIMIT 1", (ref_doc_id,))
            return cursor.fetchone() is not None
    
    @property
    def docs(self) -> Dict[str, BaseNode]:
        """Get all documents as a dictionary."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT doc_id, data FROM documents")
            docs = {}
            for row in cursor.fetchall():
                doc_id, doc_data = row
                docs[doc_id] = self._deserialize_node(json.loads(doc_data))
            return docs
    
    def persist(self, persist_path: str = "", fs: Optional[Any] = None) -> None:
        """Persist the store (no-op for SQLite as it's already persistent)."""
        logger.info(f"SQLite document store is already persistent at {self.db_path}")
    
    @classmethod
    def from_persist_dir(cls, persist_dir: str) -> "SQLiteDocumentStore":
        """Load from persist directory."""
        import os
        db_path = os.path.join(persist_dir, "docstore.db")
        return cls(db_path)

    # Async methods (delegating to sync methods for simplicity)
    async def async_add_documents(self, nodes: List[BaseNode], allow_update: bool = True) -> None:
        """Async version of add_documents."""
        self.add_documents(nodes, allow_update)

    async def adelete_document(self, doc_id: str, raise_error: bool = True) -> None:
        """Async version of delete_document."""
        self.delete_document(doc_id, raise_error)

    async def adelete_ref_doc(self, ref_doc_id: str, raise_error: bool = True) -> None:
        """Async version of delete_ref_doc."""
        self.delete_ref_doc(ref_doc_id, raise_error)

    async def adocument_exists(self, doc_id: str) -> bool:
        """Async version of document_exists."""
        return self.document_exists(doc_id)

    async def aget_all_document_hashes(self) -> Dict[str, str]:
        """Async version of get_all_document_hashes."""
        return self.get_all_document_hashes()

    async def aget_all_ref_doc_info(self) -> Dict[str, Any]:
        """Async version of get_all_ref_doc_info."""
        return self.get_all_ref_doc_info()

    async def aget_document(self, doc_id: str, raise_error: bool = True) -> Optional[BaseNode]:
        """Async version of get_document."""
        return self.get_document(doc_id, raise_error)

    async def aget_document_hash(self, doc_id: str) -> Optional[str]:
        """Async version of get_document_hash."""
        return self.get_document_hash(doc_id)

    async def aget_ref_doc_info(self, ref_doc_id: str) -> Optional[Dict[str, Any]]:
        """Async version of get_ref_doc_info."""
        return self.get_ref_doc_info(ref_doc_id)

    async def aset_document_hash(self, doc_id: str, doc_hash: str) -> None:
        """Async version of set_document_hash."""
        self.set_document_hash(doc_id, doc_hash)

    async def aset_document_hashes(self, doc_hashes: Dict[str, str]) -> None:
        """Async version of set_document_hashes."""
        self.set_document_hashes(doc_hashes)


class SQLiteIndexStore(BaseIndexStore):
    """SQLite-based index store for better performance and concurrency."""
    
    def __init__(self, db_path: str):
        """Initialize SQLite index store.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS index_structs (
                    index_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_index_updated_at ON index_structs(updated_at)")
            conn.commit()

    def _deserialize_index_struct(self, index_data: dict) -> IndexStruct:
        """Deserialize index structure data back to the correct type."""
        from llama_index.core.data_structs.data_structs import IndexStruct

        # Get the class name from the serialized data
        class_name = index_data.get("class_name", "IndexStruct")

        try:
            # Try to deserialize using the original method
            return IndexStruct.from_dict(index_data)
        except Exception as e:
            logger.warning(f"Failed to deserialize index struct with class {class_name}: {e}")

            # Check if this looks like a VectorStoreIndex structure
            if ("nodes_dict" in index_data and "doc_id_dict" in index_data and
                "embeddings_dict" in index_data):

                # Add the missing class_name for VectorStoreIndex
                index_data_copy = index_data.copy()
                index_data_copy["class_name"] = "IndexDict"

                try:
                    # Try to deserialize as IndexDict (VectorStoreIndex structure)
                    return IndexStruct.from_dict(index_data_copy)
                except Exception as e2:
                    logger.warning(f"Failed to deserialize as IndexDict: {e2}")

            # Try to use EmptyIndexStruct as final fallback
            try:
                from llama_index.core.data_structs.data_structs import EmptyIndexStruct

                # Create a minimal EmptyIndexStruct if deserialization fails
                basic_struct = EmptyIndexStruct(
                    index_id=index_data.get("index_id", "default"),
                    summary=index_data.get("summary", ""),
                )
                logger.info(f"Created fallback EmptyIndexStruct with index_id: {basic_struct.index_id}")
                return basic_struct
            except Exception as fallback_error:
                logger.error(f"Could not create fallback index struct: {fallback_error}")
                # Return None to indicate failure - this will be handled by the caller
                return None
    
    def add_index_struct(self, index_struct: IndexStruct) -> None:
        """Add index structure to the store."""
        with sqlite3.connect(self.db_path) as conn:
            index_data = index_struct.to_dict()
            index_json = json.dumps(index_data)
            
            conn.execute("""
                INSERT OR REPLACE INTO index_structs (index_id, data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (index_struct.index_id, index_json))
            conn.commit()
    
    def delete_index_struct(self, key: str) -> None:
        """Delete index structure by key."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM index_structs WHERE index_id = ?", (key,))
            conn.commit()
    
    def get_index_struct(self, struct_id: Optional[str] = None) -> Optional[IndexStruct]:
        """Get index structure by ID."""
        if struct_id is None:
            # Get the first available index struct
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT data FROM index_structs LIMIT 1")
                row = cursor.fetchone()
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT data FROM index_structs WHERE index_id = ?", (struct_id,))
                row = cursor.fetchone()

        if row is None:
            return None

        index_data = json.loads(row[0])
        result = self._deserialize_index_struct(index_data)
        if result is None:
            logger.error(f"Failed to deserialize index struct for struct_id: {struct_id}")
        return result
    
    @property
    def index_structs(self) -> Dict[str, IndexStruct]:
        """Get all index structures."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT index_id, data FROM index_structs")
            structs = {}
            for row in cursor.fetchall():
                index_id, index_data = row
                result = self._deserialize_index_struct(json.loads(index_data))
                if result is not None:
                    structs[index_id] = result
                else:
                    logger.warning(f"Skipping index struct {index_id} due to deserialization failure")
            return structs
    
    def persist(self, persist_path: str = "", fs: Optional[Any] = None) -> None:
        """Persist the store (no-op for SQLite as it's already persistent)."""
        logger.info(f"SQLite index store is already persistent at {self.db_path}")
    
    @classmethod
    def from_persist_dir(cls, persist_dir: str) -> "SQLiteIndexStore":
        """Load from persist directory."""
        import os
        db_path = os.path.join(persist_dir, "index_store.db")
        return cls(db_path)

    # Async methods (delegating to sync methods for simplicity)
    async def async_add_index_struct(self, index_struct: IndexStruct) -> None:
        """Async version of add_index_struct."""
        self.add_index_struct(index_struct)

    async def adelete_index_struct(self, key: str) -> None:
        """Async version of delete_index_struct."""
        self.delete_index_struct(key)

    async def aget_index_struct(self, struct_id: Optional[str] = None) -> Optional[IndexStruct]:
        """Async version of get_index_struct."""
        return self.get_index_struct(struct_id)

    async def async_index_structs(self) -> Dict[str, IndexStruct]:
        """Async version of index_structs property."""
        return self.index_structs
