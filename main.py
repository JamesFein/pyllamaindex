import logging

from app.settings import init_settings
from app.workflow import create_workflow
from dotenv import load_dotenv
from llama_index.server import LlamaIndexServer, UIConfig
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

logger = logging.getLogger("uvicorn")

# A path to a directory where the customized UI code is stored
COMPONENT_DIR = "components"


def create_app():
    app = LlamaIndexServer(
        workflow_factory=create_workflow,  # A factory function that creates a new workflow for each request
        ui_config=UIConfig(
            component_dir=COMPONENT_DIR,
            dev_mode=True,  # Please disable this in production 重要
            layout_dir="layout",
        ),
        logger=logger,
        env="dev",
    )

    # 添加静态文件服务
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

    # 添加根路径路由，返回清洁版前端页面
    @app.get("/")
    async def read_root():
        return FileResponse("frontend/clean.html")

    # 保留原有的健康检查路由
    app.add_api_route("/api/health", lambda: {"message": "OK"}, status_code=200)

    return app


load_dotenv()
init_settings()
app = create_app()
