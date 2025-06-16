import logging
import os

from app.settings import init_settings
from app.workflow import create_workflow
from app.index import get_index
from dotenv import load_dotenv
from llama_index.server import LlamaIndexServer, UIConfig
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("uvicorn")

# A path to a directory where the customized UI code is stored
COMPONENT_DIR = "components"


def create_app():
    app = LlamaIndexServer(
        workflow_factory=create_workflow,  # A factory function that creates a new workflow for each request
        ui_config=UIConfig(
            enabled=False,  # 禁用默认UI
        ),
        logger=logger,
        env="dev",
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js开发服务器
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # You can also add custom FastAPI routes to app
    app.add_api_route("/api/health", lambda: {"message": "OK"}, status_code=200)

    #==============================AI 添加引用API端点 start
    async def get_citation_endpoint(citation_id: str):
        """获取引用内容的API端点"""
        try:
            # 从索引中获取节点
            index = get_index()
            if not index:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Index not found"}
                )
            
            # 尝试从文档存储中获取节点
            docstore = index.docstore
            
            # 首先尝试直接获取
            try:
                node = docstore.get_node(citation_id)
                return {
                    "id": node.node_id,
                    "text": node.text,
                    "metadata": node.metadata
                }
            except:
                # 如果直接获取失败，尝试模糊匹配
                all_nodes = docstore.get_all_nodes()
                matching_nodes = [node for node in all_nodes if citation_id in node.node_id]
                
                if matching_nodes:
                    node = matching_nodes[0]
                    return {
                        "id": node.node_id,
                        "text": node.text,
                        "metadata": node.metadata
                    }
                else:
                    return JSONResponse(
                        status_code=404,
                        content={"error": f"Citation with ID {citation_id} not found"}
                    )
        except Exception as e:
            logger.error(f"Error retrieving citation: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Error retrieving citation: {str(e)}"}
            )

    # 注册引用API端点
    app.add_api_route("/api/citation/{citation_id}", get_citation_endpoint, methods=["GET"])
    # ==============================AI 添加引用API端点 end

    # 检查是否有Next.js构建的文件
    nextjs_build_dir = os.path.join(COMPONENT_DIR, "out")
    if os.path.exists(nextjs_build_dir):
        # 生产模式：挂载Next.js构建的静态文件
        app.mount("/", StaticFiles(directory=nextjs_build_dir, html=True), name="nextjs-build")
        logger.info(f"Serving Next.js build from {nextjs_build_dir}")
    else:
        # 开发模式：Next.js开发服务器运行在3000端口
        # 这里只提供API服务，前端由Next.js dev server提供
        logger.info("Development mode: Next.js should be running on port 3000")

    return app





load_dotenv()
init_settings()
app = create_app()
