from typing import Optional

from app.index import get_index
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.settings import Settings
from llama_index.server.api.models import ChatRequest
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.tools import FunctionTool


def create_workflow(chat_request: Optional[ChatRequest] = None) -> AgentWorkflow:
    index = get_index(chat_request=chat_request)
    if index is None:
        raise RuntimeError(
            "Index not found! Please run `uv run generate` to index the data first."
        )

    # Create a CitationQueryEngine that generates single responses with citations
    citation_query_engine = CitationQueryEngine.from_args(
        index,
        similarity_top_k=3,  # Retrieve top 3 relevant chunks
        citation_chunk_size=1024,  # Larger chunks for better context
    )

    # Create a custom tool function that uses the citation query engine
    def query_with_citations(input: str) -> str:
        """Query the knowledge base and return an answer with citations."""
        response = citation_query_engine.query(input)
        return str(response)

    # Create a function tool from our custom function
    query_tool = FunctionTool.from_defaults(
        fn=query_with_citations,
        name="query_index",
        description="Query the knowledge base to answer questions about financial topics with citations."
    )

    # Define the system prompt for the agent
    system_prompt = """You are a helpful financial knowledge assistant.

Use the query_index tool to search for information in the knowledge base when answering questions.
The tool will return answers with proper citations in the format [citation:id].
Always use the tool's response directly without modifying the citations."""

    return AgentWorkflow.from_tools_or_functions(
        tools_or_functions=[query_tool],
        llm=Settings.llm,
        system_prompt=system_prompt,
    )
