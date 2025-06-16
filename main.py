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
from fastapi import UploadFile, File, HTTPException
from typing import List
import asyncio
import uuid
import shutil

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

    # ==============================AI 添加文档管理API端点 start
    async def get_documents_endpoint():
        """获取文档列表的API端点 - 返回文件级别的文档，而不是文本块"""
        try:
            from app.storage_config import load_storage_context
            from app.index import STORAGE_DIR

            storage_context = load_storage_context(STORAGE_DIR)
            if not storage_context:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Storage context not found"}
                )

            # 获取文件列表（而不是文档块列表）
            files = storage_context.docstore.get_files_with_metadata()

            return JSONResponse(content={
                "documents": files,  # 保持API兼容性，但实际返回的是文件
                "total": len(files)
            })

        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to get documents: {str(e)}"}
            )

    async def upload_documents_endpoint(files: List[UploadFile] = File(...)):
        """上传文档的API端点 - 使用新的文件管理结构"""
        try:
            import hashlib
            from app.storage_config import get_storage_context
            from app.index import STORAGE_DIR
            from llama_index.core.readers import SimpleDirectoryReader
            from llama_index.core.node_parser import SentenceSplitter
            from llama_index.core.indices import VectorStoreIndex

            # 确保data目录存在
            data_dir = os.environ.get("DATA_DIR", "data")
            os.makedirs(data_dir, exist_ok=True)

            upload_results = []

            for file in files:
                try:
                    # 直接使用原始文件名，同名文件视为同一份文件
                    file_path = os.path.join(data_dir, file.filename)

                    # 使用文件名的哈希作为文件ID，确保同名文件有相同的ID
                    file_id = f"file_{hashlib.md5(file.filename.encode()).hexdigest()[:8]}"

                    # 获取存储上下文
                    storage_context = get_storage_context(STORAGE_DIR)

                    # 检查是否存在同名文件，如果存在则完全删除旧文件
                    existing_file_info = storage_context.docstore.get_file_info(file_id)
                    if existing_file_info:
                        logger.info(f"Found existing file with same name: {file.filename}, deleting old version...")

                        # 1. 删除文件系统中的旧文件
                        old_file_path = existing_file_info['path']
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                            logger.info(f"Deleted old file: {old_file_path}")

                        # 2. 删除数据库中的文件记录和所有相关文档块
                        storage_context.docstore.delete_file_and_chunks(file_id)
                        logger.info(f"Deleted old file record and chunks for: {file.filename}")

                        # 3. 重新持久化存储上下文以清理向量索引
                        storage_context.persist(STORAGE_DIR)

                    # 保存新文件
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)

                    # 获取文件信息
                    file_size = os.path.getsize(file_path)
                    file_type = file.content_type or "text/plain"

                    # 计算文件哈希
                    file_hash = hashlib.md5()
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            file_hash.update(chunk)
                    file_hash_str = file_hash.hexdigest()

                    # 1. 先添加文件记录到files表
                    success = storage_context.docstore.add_file_record(
                        file_id=file_id,
                        file_name=file.filename,
                        file_path=file_path,
                        file_size=file_size,
                        file_type=file_type,
                        file_hash=file_hash_str
                    )

                    if not success:
                        upload_results.append({
                            "filename": file.filename,
                            "status": "error",
                            "message": "Failed to create file record"
                        })
                        os.remove(file_path)
                        continue

                    # 2. 处理文档内容
                    reader = SimpleDirectoryReader(input_files=[file_path])
                    documents = reader.load_data()

                    if not documents:
                        upload_results.append({
                            "filename": file.filename,
                            "status": "error",
                            "message": "Failed to read document content"
                        })
                        # 清理文件记录和文件
                        storage_context.docstore.delete_file_and_chunks(file_id)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        continue

                    # 3. 解析为节点
                    parser = SentenceSplitter()
                    nodes = parser.get_nodes_from_documents(documents)

                    # 4. 为每个节点添加文件关联信息
                    for chunk_index, node in enumerate(nodes):
                        # 添加文件元数据
                        if hasattr(node, 'metadata'):
                            node.metadata.update({
                                'file_id': file_id,
                                'file_name': file.filename,
                                'file_size': file_size,
                                'file_type': file_type,
                                'file_path': file_path,
                                'chunk_index': chunk_index + 1
                            })
                        else:
                            node.metadata = {
                                'file_id': file_id,
                                'file_name': file.filename,
                                'file_size': file_size,
                                'file_type': file_type,
                                'file_path': file_path,
                                'chunk_index': chunk_index + 1
                            }

                    # 5. 添加到文档存储（这会更新documents表）
                    storage_context.docstore.add_documents(nodes, file_metadata={
                        'file_id': file_id,
                        'file_name': file.filename,
                        'file_size': file_size,
                        'file_type': file_type
                    })

                    # 6. 更新向量索引
                    VectorStoreIndex(nodes, storage_context=storage_context)
                    storage_context.persist(STORAGE_DIR)

                    upload_results.append({
                        "filename": file.filename,
                        "status": "success",
                        "message": f"Successfully processed {len(nodes)} chunks",
                        "chunks": len(nodes),
                        "file_id": file_id
                    })

                except Exception as e:
                    logger.error(f"Error processing file {file.filename}: {e}")
                    upload_results.append({
                        "filename": file.filename,
                        "status": "error",
                        "message": str(e)
                    })

                    # 清理失败的文件
                    if 'file_path' in locals() and os.path.exists(file_path):
                        os.remove(file_path)

            return JSONResponse(content={
                "results": upload_results,
                "total_files": len(files),
                "successful": len([r for r in upload_results if r["status"] == "success"])
            })

        except Exception as e:
            logger.error(f"Error uploading documents: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to upload documents: {str(e)}"}
            )

    async def delete_document_endpoint(file_id: str):
        """删除文档的API端点 - 删除整个文件及其所有文本块"""
        try:
            from app.storage_config import load_storage_context
            from app.index import STORAGE_DIR

            storage_context = load_storage_context(STORAGE_DIR)
            if not storage_context:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Storage context not found"}
                )

            # 获取文件信息
            file_info = storage_context.docstore.get_file_info(file_id)
            if not file_info:
                return JSONResponse(
                    status_code=404,
                    content={"error": "File not found"}
                )

            # 删除文件系统中的文件
            file_path = file_info['path']
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")

            # 从数据库删除文件记录和所有相关的文档块
            success = storage_context.docstore.delete_file_and_chunks(file_id)

            if success:
                # 重新持久化存储上下文
                storage_context.persist(STORAGE_DIR)

                return JSONResponse(content={
                    "message": "File and all chunks deleted successfully",
                    "file_id": file_id,
                    "file_name": file_info['name']
                })
            else:
                return JSONResponse(
                    status_code=404,
                    content={"error": "File not found in database"}
                )

        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to delete file: {str(e)}"}
            )

    # 注册文档管理API端点
    app.add_api_route("/api/documents", get_documents_endpoint, methods=["GET"])
    app.add_api_route("/api/documents/upload", upload_documents_endpoint, methods=["POST"])
    app.add_api_route("/api/documents/{file_id}", delete_document_endpoint, methods=["DELETE"])
    # ==============================AI 添加文档管理API端点 end

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
