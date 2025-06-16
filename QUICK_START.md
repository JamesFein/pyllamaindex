# 🚀 PyLlamaIndex 快速启动指南

## ✅ 迁移完成！

已成功将前端从 Vue.js 迁移到 Next.js + LlamaIndex Chat UI！

## 🎯 新架构

### 前端 (Next.js + LlamaIndex Chat UI)

- **地址**: http://localhost:3000
- **技术栈**: Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **特性**:
  - 使用官方@llamaindex/chat-ui 组件
  - 支持 Vercel AI SDK 流式处理
  - 智能引用显示（hover tooltip）
  - 响应式设计

### 后端 (FastAPI + LlamaIndex)

- **地址**: http://localhost:8000
- **技术栈**: FastAPI + LlamaIndex + SQLite + ChromaDB
- **特性**:
  - Agent 工作流
  - 文档索引和检索
  - 引用系统
  - CORS 支持

## 🚀 启动步骤

### 1. 启动后端

```bash
# 在项目根目录
uv run fastapi dev --port 8000
```

### 2. 启动前端

```bash
# 方法1：使用批处理脚本
cd components
start-dev.bat

# 方法2：手动启动
cd components
npm run dev
```

### 3. 访问应用

- 前端界面: http://localhost:3000
- 后端 API 文档: http://localhost:8000/docs

## 🎨 新功能特性

### 1. 现代化聊天界面

- 基于 shadcn/ui 的美观设计
- 支持 Markdown 渲染
- 实时流式响应
- 加载状态指示

### 2. 智能引用系统

- 自动解析`[citation:id]`格式
- 显示序号标记 [1] [2] [3]
- Hover 显示引用内容
- 滚动式 tooltip
- 文档名称和内容预览

### 3. 响应式设计

- 移动端友好
- 自适应布局
- 现代化 UI 组件

### 4. 开发体验

- TypeScript 类型安全
- 热重载开发
- ESLint 代码检查
- 自动格式化

## 🔧 开发说明

### 项目结构

```
pyllamaindex/
├── app/                    # FastAPI后端
├── components/             # Next.js前端
│   ├── app/               # Next.js App Router
│   ├── package.json       # 前端依赖
│   └── README.md          # 前端文档
├── data/                  # 文档数据
├── storage/               # 索引存储
└── main.py               # FastAPI入口
```

### 自定义组件

- `CitationTooltip`: 引用 hover 效果
- `CustomChatMessage`: 消息渲染和引用解析

### API 集成

- 通过 Next.js rewrites 代理 API 请求
- 支持 CORS 跨域访问
- 自动处理流式响应

## 🎉 迁移优势

### 相比之前的 Vue.js 版本：

1. **更好的流式处理**: 使用 Vercel AI SDK 自动处理复杂流式数据
2. **类型安全**: TypeScript 提供完整类型检查
3. **组件复用**: 使用官方维护的聊天组件
4. **开发效率**: 热重载、错误提示、自动优化
5. **未来兼容**: 与 LlamaIndex 生态系统保持同步
6. **更好的引用体验**: 智能 hover tooltip 替代点击弹窗

## 🐛 故障排除

### 常见问题

1. **端口冲突**

   - 前端: 3001 端口
   - 后端: 8000 端口
   - 确保端口未被占用

2. **API 连接失败**

   - 检查 CORS 配置
   - 确认后端服务运行正常

3. **引用不显示**
   - 检查后端引用 API 端点
   - 确认数据格式正确

### 调试模式

- 浏览器控制台查看详细日志
- 后端日志查看 API 请求
- 网络面板检查 API 响应

## 🎯 下一步

1. 测试聊天功能和引用显示
2. 根据需要调整样式和布局
3. 添加更多自定义功能
4. 优化性能和用户体验

---

**🎉 恭喜！您已成功迁移到现代化的 Next.js + LlamaIndex Chat UI 架构！**
