import logging
import os

from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def generate_index():
    """
    Index the documents in the data directory using SQLite and ChromaDB.
    """
    from app.index import STORAGE_DIR
    from app.settings import init_settings
    from app.storage_config import get_storage_context
    from llama_index.core.indices import (
        VectorStoreIndex,
    )
    from llama_index.core.readers import SimpleDirectoryReader

    load_dotenv()
    init_settings()

    logger.info("Creating new index with SQLite and ChromaDB storage")

    # Create storage context with SQLite and ChromaDB
    storage_context = get_storage_context(STORAGE_DIR)

    # load the documents and create the index
    reader = SimpleDirectoryReader(
        os.environ.get("DATA_DIR", "data"),
        recursive=True,
    )
    documents = reader.load_data()

    # Parse documents into nodes
    from llama_index.core.node_parser import SentenceSplitter
    import hashlib

    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents(documents)

    logger.info(f"Parsed {len(documents)} documents into {len(nodes)} nodes")

    # Process each document and its nodes to add file metadata
    processed_nodes = []
    for document in documents:
        # Extract file information from document metadata
        file_path = document.metadata.get('file_path', '')
        file_name = document.metadata.get('file_name', os.path.basename(file_path))

        # Generate file_id based on file_name (consistent with upload logic)
        file_id = f"file_{hashlib.md5(file_name.encode()).hexdigest()[:8]}"

        # Get file stats
        try:
            file_stats = os.stat(file_path) if file_path and os.path.exists(file_path) else None
            file_size = file_stats.st_size if file_stats else 0
        except:
            file_size = 0

        file_type = "text/plain"  # Default for txt files

        # Add file record to the files table
        storage_context.docstore.add_file_record(
            file_id=file_id,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            file_hash=""
        )

        # Find nodes that belong to this document
        doc_nodes = [node for node in nodes if node.ref_doc_id == document.doc_id]

        # Add file metadata to each node
        for i, node in enumerate(doc_nodes):
            if not hasattr(node, 'metadata'):
                node.metadata = {}

            node.metadata.update({
                'file_id': file_id,
                'file_name': file_name,
                'file_size': file_size,
                'file_type': file_type,
                'chunk_index': i
            })
            processed_nodes.append(node)

    logger.info(f"Processed {len(processed_nodes)} nodes with file metadata")

    # Add nodes to docstore manually
    storage_context.docstore.add_documents(processed_nodes)

    # Create index with custom storage context
    index = VectorStoreIndex(
        processed_nodes,
        storage_context=storage_context,
        show_progress=True,
    )

    # Persist the storage context (this will save to SQLite and ChromaDB)
    storage_context.persist(STORAGE_DIR)
    logger.info(f"Finished creating new index. Stored in {STORAGE_DIR} using SQLite and ChromaDB")


def generate_ui_for_workflow():
    """
    Generate UI for UIEventData event in app/workflow.py
    """
    import asyncio

    from main import COMPONENT_DIR

    # To generate UI components for additional event types,
    # import the corresponding data model (e.g., MyCustomEventData)
    # and run the generate_ui_for_workflow function with the imported model.
    # Make sure the output filename of the generated UI component matches the event type (here `ui_event`)
    try:
        from app.workflow import UIEventData  # type: ignore
    except ImportError:
        raise ImportError("Couldn't generate UI component for the current workflow.")
    from llama_index.server.gen_ui import generate_event_component

    # works also well with Claude 3.7 Sonnet or Gemini Pro 2.5
    llm = OpenAI(model="gpt-4.1")
    code = asyncio.run(generate_event_component(event_cls=UIEventData, llm=llm))
    with open(f"{COMPONENT_DIR}/ui_event.jsx", "w") as f:
        f.write(code)
