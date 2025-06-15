from typing import Optional
import json

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

        # Extract citation information from source nodes
        citation_data = {}
        if hasattr(response, 'source_nodes') and response.source_nodes:
            for i, node in enumerate(response.source_nodes):
                # Get node ID for citation mapping
                node_id = node.node_id if hasattr(node, 'node_id') else str(i)

                # Extract filename from metadata
                filename = "未知文档"
                if hasattr(node, 'metadata') and node.metadata:
                    filename = node.metadata.get('file_name',
                              node.metadata.get('filename',
                              node.metadata.get('source', '未知文档')))

                # Get similarity score
                similarity_score = 0.0
                if hasattr(node, 'score') and node.score is not None:
                    similarity_score = float(node.score)

                # Get document content (保留完整内容)
                content = ""
                if hasattr(node, 'text') and node.text:
                    content = node.text
                elif hasattr(node, 'get_content') and callable(node.get_content):
                    content = node.get_content()

                citation_data[node_id] = {
                    "rank": i + 1,
                    "filename": filename,
                    "content": content,
                    "similarity_score": similarity_score
                }

        # Convert response to string and append citation metadata
        response_text = str(response)

        # Add citation metadata as a JSON comment at the end
        if citation_data:
            # Clean the content to avoid JSON parsing issues (保留完整内容)
            cleaned_citation_data = {}
            for node_id, data in citation_data.items():
                # 保留完整内容，只清理特殊字符
                clean_content = data["content"].replace('\r', '').replace('\n', ' ').replace('"', '\\"')
                cleaned_citation_data[node_id] = {
                    "rank": data["rank"],
                    "filename": data["filename"],
                    "content": clean_content,
                    "similarity_score": data["similarity_score"]
                }

            citation_json = json.dumps(cleaned_citation_data, ensure_ascii=False, indent=2)
            response_text += f"\n\n<!-- CITATION_DATA: {citation_json} -->"

        return response_text

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
