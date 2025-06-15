# API 流式输出与引用展示机制解析

> 针对 `pyllama` 项目后端 (FastAPI + `llama_index.server`) 的源码调研报告，聚焦于：
> 1. **如何实现向浏览器的流式输出**；
> 2. **如何将引用信息（文档名、块编号、块内容）随答案一并返回浏览器**；
> 3. **若要替换成 Vue 前端，需要对接哪些接口**。

---

## 1. 整体架构速览

```
┌──────────────┐    HTTP(S)    ┌──────────────┐
│   Vue/App    │◀────────────▶│  FastAPI App │
└──────────────┘  (JSON/Stream)└──────────────┘
                           ▲
                           │Invoke
                 ┌────────────────────┐
                 │  LlamaIndex Server │
                 └────────────────────┘
                           ▲
                           │Query / Citation
                 ┌────────────────────┐
                 │ VectorStoreIndex    │
                 └────────────────────┘
```

* `main.py` 通过 `LlamaIndexServer` 创建 **FastAPI** 应用，并**自动挂载**了一组 API：
  * `POST /api/chat`  —— 同步一次性返回
  * `POST /api/chat/stream` —— **Server-Sent Events**(SSE) 流式返回
  * 其他静态资源、健康检查、自定义路由
* 默认 UI 是 Next.js 导出的静态站点（位于 `.ui/`）。你打算替换成 Vue，只需面向上面两条 API 即可，无需改动后端。

## 2. 流式输出实现细节

1. **触发点**  
   浏览器向 `POST /api/chat/stream` 发送 JSON：

   ```jsonc
   {
     "messages": [ {"content": "...", "role": "user"} ]
   }
   ```

2. **FastAPI 端**  
   `LlamaIndexServer` 拦截该请求，调用 `workflow_factory`（即 `create_workflow`）。

3. **LlamaIndex 端**  
   `AgentWorkflow` 在调用 LLM 时使用支持 **token stream** 的 `Settings.llm`。

4. **回调链**  
   LlamaIndex 内部通过 `CallbackManager` 将新 token 逐个推送给 `LlamaIndexServer` 实现的回调，后者再写入 `EventSourceResponse`（SSE）。格式形如：

   ```text
   data: {"delta":"新 token"}\n\n
   data: {"delta":"."}\n\n
   ...
   data: [DONE]\n\n
   ```

5. **浏览器端**  
   前端通过 `fetch` + `ReadableStream`（或 `EventSource`）实时接收 `data:` 片段并渲染。

> 与 LlamaIndex 的关系：后端 **不自行拆分 token**，而是完全依赖 LlamaIndex 的流式代理能力；`LlamaIndexServer` 只负责把 token 转成 SSE 并 relay 到浏览器。

## 3. 引用信息的生成与传递

1. **启用方式**  
   在 `app/workflow.py`：

   ```python
   query_tool = enable_citation(get_query_engine_tool(index=index))
   ```

   `enable_citation()` 会包装 `QueryEngineTool`，让其在执行查询后，在返回对象里附带 `source_nodes`（每个节点对应一个文档块）。

2. **数据结构**  
   每个 `NodeWithScore` 包含：
   * `node.id_`  —— 即 **块编号**（chunk id）
   * `node.ref_doc_id` —— 源文档 ID
   * `node.metadata["file_name"]` —— **文件名**（如 `101.pdf`）
   * `node.text` —— **块内容**（少量文字）

3. **序列化**  
   `LlamaIndexServer` 将这些 `source_nodes` 转为简化的 JSON 数组 `citations`，然后：

   * 在 **同步接口**：直接放入响应 JSON 的 `citations` 字段。
   * 在 **流式接口**：在流末尾追加一次特殊包：

     ```text
     data: {"citations": [...]}\n\n
     data: [DONE]\n\n
     ```

4. **前端渲染**  
   原始 Next.js UI 会在流结束后解析该包，展示卡片：文件标题 + 块号列表，并在 hover 时弹出块内容。

## 4. 换成 Vue 前端的接入要点

1. **复制请求逻辑**：
   ```ts
   const resp = await fetch("/api/chat/stream", {
     method: "POST",
     headers: { "Content-Type": "application/json" },
     body: JSON.stringify({ messages })
   });
   const reader = resp.body!.getReader();
   // 逐块解析 SSE，同步渲染 token
   ```

2. **处理两类数据片段**：
   * `{"delta": "..."}` —— 追加到回答文本
   * `{"citations": [...]}` —— 保存引用信息并渲染侧边栏/弹框

3. **可复用的解析器**：可用正则捕获 `/^data: (.*)\n\n/` 提取 JSON 字符串，再用 `JSON.parse`。

4. **样式与交互**：引用渲染可参考现有 `.ui/index.html` 内的实现逻辑（卡片 + 段号），亦可自行设计。

---

## 5. 结论

* **流式输出** 依赖于 LlamaIndex 的 token streaming + `LlamaIndexServer` 的 SSE 转发，不需要自行管理 websocket。
* **引用信息** 通过 `enable_citation()` 注入，无需你手动拼装；前端只要识别最终 `citations` 数据即可。
* **Vue 迁移** 只涉及前端层，后端接口保持不变；重点是解析 SSE 与渲染逻辑。


