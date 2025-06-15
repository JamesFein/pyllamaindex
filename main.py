import logging
import json

from app.settings import init_settings
from app.workflow import create_workflow
from app.streaming import create_streaming_response
from dotenv import load_dotenv
from llama_index.server import LlamaIndexServer, UIConfig
from llama_index.server.api.models import ChatRequest
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Request

logger = logging.getLogger("uvicorn")

# A path to a directory where the customized UI code is stored
COMPONENT_DIR = "components"


def create_app():
    app = LlamaIndexServer(
        workflow_factory=create_workflow,
        ui_config=UIConfig(
            component_dir=COMPONENT_DIR,
            dev_mode=True,
            layout_dir="layout",
        ),
        logger=logger,
        env="dev",
    )

    # 添加新的前端静态文件服务
    app.mount("/static", StaticFiles(directory="external_ui"), name="static")

    # 添加根路径路由，返回新的前端页面
    @app.get("/")
    async def read_root():
        return FileResponse("external_ui/index.html")

    # 添加测试页面路由
    @app.get("/test")
    async def test_page():
        return FileResponse("test_frontend_streaming.html")

    # 保留原有的健康检查路由
    app.add_api_route("/api/health", lambda: {"message": "OK"}, status_code=200)

    # 定义流式聊天API端点函数
    async def stream_chat(request: Request, data: str):
        """流式聊天API端点"""
        try:
            # 解析请求数据
            import json
            chat_data = json.loads(data)

            # 创建ChatRequest对象
            from llama_index.server.api.models import ChatRequest
            chat_request = ChatRequest(**chat_data)

            # 创建工作流
            workflow = create_workflow(chat_request)

            # 获取最后一条用户消息
            user_message = ""
            if chat_request.messages:
                user_message = chat_request.messages[-1].content

            # 运行工作流获取响应
            response = await workflow.run(user_msg=user_message)

            # 从AgentWorkflow响应中提取文本内容
            response_text = ""
            if hasattr(response, 'response') and hasattr(response.response, 'blocks'):
                # 从blocks中提取文本
                for block in response.response.blocks:
                    if hasattr(block, 'text'):
                        response_text += block.text
            else:
                response_text = str(response)

            # 检查是否有工具调用结果包含引用数据
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    if hasattr(tool_call, 'tool_output') and hasattr(tool_call.tool_output, 'content'):
                        tool_content = tool_call.tool_output.content
                        # 如果工具输出包含引用数据，使用它
                        if "CITATION_DATA:" in tool_content:
                            response_text = tool_content
                            break

            # 返回流式响应
            return await create_streaming_response(response_text, request)

        except Exception as e:
            logger.error(f"Error in stream chat: {e}")
            # 返回错误的流式响应
            error_response = f"抱歉，发生了错误：{str(e)}"
            return await create_streaming_response(error_response, request)

    # 添加流式聊天API端点
    app.add_api_route("/api/chat/stream", stream_chat, methods=["GET"])

    return app


load_dotenv()
init_settings()
app = create_app()
