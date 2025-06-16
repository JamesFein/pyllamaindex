# 前端迁移计划：从Vue.js到Next.js + LlamaIndex Chat UI

## 方案选择：Next.js + @llamaindex/chat-ui

### 为什么选择Next.js而不是纯React？

1. **官方支持**：LlamaIndex Chat UI专为Next.js设计
2. **流式处理**：完美支持Vercel AI SDK的流式协议
3. **开发体验**：内置TypeScript、热重载、优化功能
4. **生态系统**：与create-llama项目架构一致

## 实施步骤

### 第一阶段：环境准备

1. **创建Next.js前端项目**
   ```bash
   # 在项目根目录创建frontend文件夹
   npx create-next-app@latest frontend --typescript --tailwind --eslint --app
   cd frontend
   ```

2. **安装LlamaIndex Chat UI**
   ```bash
   npm install @llamaindex/chat-ui ai react react-dom
   ```

3. **配置Tailwind CSS**
   - 更新`tailwind.config.ts`包含chat-ui组件
   - 添加主题变量到`globals.css`

### 第二阶段：基础聊天界面

1. **创建主聊天页面** (`app/page.tsx`)
   - 使用`ChatSection`组件
   - 集成`useChat` hook
   - 配置API端点为`http://localhost:8000/api/chat`

2. **处理CORS问题**
   - 在FastAPI后端添加CORS中间件
   - 允许前端域名访问

### 第三阶段：流式输出处理

1. **实现Vercel AI SDK兼容的流式处理**
   - 后端返回符合Vercel流式协议的响应
   - 前端使用`useChat`自动处理流式数据

2. **引用功能迁移**
   - 实现引用数据的解析和显示
   - 添加hover tooltip功能
   - 保持序号显示功能

### 第四阶段：样式和功能完善

1. **样式迁移**
   - 将现有CSS样式转换为Tailwind类
   - 实现引用样式的独立模块
   - 添加响应式设计

2. **功能增强**
   - 文件上传支持
   - 消息历史管理
   - 错误处理和加载状态

## 项目结构

```
pyllamaindex/
├── app/                    # FastAPI后端
├── components/            # 当前Vue.js前端（保留作为备份）
├── frontend/              # 新的Next.js前端
│   ├── app/
│   │   ├── api/          # Next.js API路由（如果需要）
│   │   ├── components/   # React组件
│   │   ├── page.tsx      # 主聊天页面
│   │   └── layout.tsx    # 布局组件
│   ├── public/
│   ├── styles/
│   └── package.json
├── data/
├── storage/
└── main.py               # FastAPI服务器
```

## 开发流程

### 开发模式
```bash
# 终端1：启动FastAPI后端
uv run fastapi dev --port 8000

# 终端2：启动Next.js前端
cd frontend
npm run dev
```

### 生产模式
```bash
# 构建前端
cd frontend
npm run build

# 配置FastAPI服务静态文件
# 修改main.py挂载构建后的文件
```

## 技术栈对比

| 功能 | 当前Vue.js | 新Next.js |
|------|------------|------------|
| 框架 | Vue 3 | Next.js 14 + React 18 |
| 样式 | 自定义CSS | Tailwind CSS |
| 流式处理 | 手动实现 | Vercel AI SDK |
| 引用显示 | 自定义实现 | Chat UI组件 |
| 类型安全 | 无 | TypeScript |
| 开发工具 | 基础 | 完整工具链 |

## 迁移优势

1. **更好的流式处理**：自动处理复杂的流式数据格式
2. **类型安全**：TypeScript提供完整的类型检查
3. **组件复用**：使用官方维护的聊天组件
4. **开发效率**：热重载、错误提示、自动优化
5. **未来兼容**：与LlamaIndex生态系统保持同步

## 风险评估

### 低风险
- 后端API保持不变
- 可以并行开发，不影响现有功能
- 可以逐步迁移功能

### 需要注意
- CORS配置
- 流式数据格式兼容性
- 引用功能的完整迁移

## 时间估算

- **第一阶段**：1-2小时（环境搭建）
- **第二阶段**：2-3小时（基础功能）
- **第三阶段**：3-4小时（流式处理）
- **第四阶段**：2-3小时（样式完善）

**总计**：8-12小时完成完整迁移

## 下一步行动

1. 确认方案选择
2. 开始第一阶段：创建Next.js项目
3. 逐步实施各个阶段
4. 测试和优化
