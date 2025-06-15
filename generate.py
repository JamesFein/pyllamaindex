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
    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents(documents)

    logger.info(f"Parsed {len(documents)} documents into {len(nodes)} nodes")

    # Add nodes to docstore manually
    storage_context.docstore.add_documents(nodes)

    # Create index with custom storage context
    index = VectorStoreIndex(
        nodes,
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
