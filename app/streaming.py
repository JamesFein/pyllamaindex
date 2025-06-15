"""
流式响应处理模块
使用 sse-starlette 来优化大模型返回信息的处理
"""
import json
import asyncio
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from sse_starlette import EventSourceResponse, ServerSentEvent

logger = logging.getLogger("uvicorn")


class StreamingResponseProcessor:
    """流式响应处理器"""
    
    def __init__(self):
        self.citation_data = {}
    
    async def process_streaming_response(
        self, 
        response_text: str, 
        request=None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        处理流式响应，将大文本分块发送
        
        Args:
            response_text: 完整的响应文本
            request: FastAPI请求对象（用于检测客户端断开连接）
        
        Yields:
            包含数据的字典，用于SSE传输
        """
        try:
            # 解析引用数据
            citation_data = self._extract_citation_data(response_text)
            clean_text = self._clean_response_text(response_text)
            
            # 首先发送引用数据
            if citation_data:
                yield {
                    "data": json.dumps({
                        "type": "citations",
                        "citations": citation_data
                    }, ensure_ascii=False),
                    "event": "citation_data"
                }
                await asyncio.sleep(0.01)  # 小延迟确保顺序
            
            # 将文本分块发送
            chunk_size = 100  # 每块字符数
            text_chunks = self._split_text_into_chunks(clean_text, chunk_size)
            
            for i, chunk in enumerate(text_chunks):
                # 检查客户端是否断开连接
                if request and await request.is_disconnected():
                    logger.info("Client disconnected, stopping stream")
                    break
                
                yield {
                    "data": json.dumps({
                        "type": "text_chunk",
                        "chunk": chunk,
                        "chunk_index": i,
                        "is_final": i == len(text_chunks) - 1
                    }, ensure_ascii=False),
                    "event": "text_chunk"
                }
                
                # 添加小延迟模拟流式效果
                await asyncio.sleep(0.05)
            
            # 发送完成信号
            yield {
                "data": json.dumps({
                    "type": "complete",
                    "message": "Response complete"
                }, ensure_ascii=False),
                "event": "complete"
            }
            
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield {
                "data": json.dumps({
                    "type": "error",
                    "error": str(e)
                }, ensure_ascii=False),
                "event": "error"
            }
    
    def _extract_citation_data(self, response_text: str) -> Dict[str, Any]:
        """从响应文本中提取引用数据"""
        import re
        
        # 查找引用数据注释
        citation_pattern = r'<!-- CITATION_DATA:\s*(.*?)\s*-->'
        match = re.search(citation_pattern, response_text, re.DOTALL)
        
        if match:
            try:
                citation_json_str = match.group(1)
                return json.loads(citation_json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse citation data: {e}")
                return {}
        
        return {}
    
    def _clean_response_text(self, response_text: str) -> str:
        """清理响应文本，移除引用数据注释"""
        import re
        
        # 移除引用数据注释
        clean_text = re.sub(r'<!-- CITATION_DATA:.*?-->', '', response_text, flags=re.DOTALL)
        return clean_text.strip()
    
    def _split_text_into_chunks(self, text: str, chunk_size: int) -> list:
        """将文本分割成指定大小的块"""
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks


async def create_streaming_response(
    response_text: str, 
    request=None
) -> EventSourceResponse:
    """
    创建流式SSE响应
    
    Args:
        response_text: 完整的响应文本
        request: FastAPI请求对象
    
    Returns:
        EventSourceResponse对象
    """
    processor = StreamingResponseProcessor()
    
    async def event_generator():
        async for data in processor.process_streaming_response(response_text, request):
            yield ServerSentEvent(
                data=data["data"],
                event=data["event"]
            )
    
    return EventSourceResponse(
        event_generator(),
        ping=15,  # 每15秒发送ping
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


def process_citation_text(text: str, citations: Dict[str, Any]) -> str:
    """
    处理文本中的引用标记，替换为带有排名的引用数字
    
    Args:
        text: 原始文本
        citations: 引用数据字典
    
    Returns:
        处理后的HTML文本
    """
    import re
    
    # 创建引用映射（按排名排序）
    citation_map = {}
    for node_id, data in citations.items():
        rank = data.get("rank", 1)
        citation_map[rank] = {
            "node_id": node_id,
            "filename": data.get("filename", "未知文档"),
            "content": data.get("content", ""),
            "similarity_score": data.get("similarity_score", 0.0)
        }
    
    # 查找所有的Source引用模式
    source_pattern = r'Source (\d+):'
    
    def replace_source(match):
        source_num = int(match.group(1))
        if source_num in citation_map:
            citation_info = citation_map[source_num]
            # 创建引用HTML
            citation_data = json.dumps(citation_info).replace('"', '&quot;')
            return f'<span class="citation-number" data-rank="{source_num}" data-citation="{citation_data}">{source_num}</span>'
        return match.group(0)
    
    # 替换所有Source引用
    processed_text = re.sub(source_pattern, replace_source, text)
    
    return processed_text
