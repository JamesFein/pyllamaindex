# PyLlamaIndex Frontend (Next.js + LlamaIndex Chat UI)

这是使用Next.js和LlamaIndex Chat UI构建的现代化聊天界面。

## 功能特性

- ✅ 基于Next.js 15和React 19
- ✅ 使用@llamaindex/chat-ui组件库
- ✅ 支持Vercel AI SDK的流式处理
- ✅ 智能引用显示（hover tooltip）
- ✅ TypeScript类型安全
- ✅ Tailwind CSS样式
- ✅ 响应式设计

## 开发环境启动

### 方法1：使用批处理脚本（推荐）
```bash
# 在components目录下运行
start-dev.bat
```

### 方法2：手动启动
```bash
# 1. 安装依赖
cd components
npm install

# 2. 启动开发服务器
npm run dev
```

### 3. 启动后端
在另一个终端中：
```bash
# 在项目根目录
uv run fastapi dev --port 8000
```

## 访问地址

- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000

## 项目结构

```
components/
├── app/                    # Next.js App Router
│   ├── components/         # 自定义React组件
│   │   ├── CitationTooltip.tsx    # 引用提示组件
│   │   └── CustomChatMessage.tsx  # 自定义消息组件
│   ├── globals.css         # 全局样式
│   ├── layout.tsx          # 根布局
│   └── page.tsx            # 主聊天页面
├── public/                 # 静态资源
├── package.json            # 依赖配置
├── next.config.js          # Next.js配置
├── tailwind.config.ts      # Tailwind配置
└── tsconfig.json           # TypeScript配置
```

## 核心功能

### 1. 流式聊天
- 使用Vercel AI SDK的`useChat` hook
- 自动处理流式响应
- 实时消息更新

### 2. 引用系统
- 自动解析`[citation:id]`格式的引用
- 显示序号标记
- Hover显示引用内容
- 滚动式tooltip

### 3. 响应式设计
- 移动端友好
- 自适应布局
- 现代化UI

## 生产部署

### 构建静态文件
```bash
cd components
npm run build
npm run export  # 生成静态文件到out目录
```

### 部署到FastAPI
构建完成后，静态文件会在`components/out`目录中，FastAPI会自动检测并提供服务。

## 开发说明

### 自定义组件
- `CitationTooltip`: 处理引用的hover效果
- `CustomChatMessage`: 自定义消息渲染，支持引用解析

### 样式定制
- 主题变量在`app/globals.css`中定义
- 引用样式可在CSS中自定义
- 使用Tailwind CSS类进行快速样式调整

### API集成
- 通过Next.js的rewrites功能代理API请求
- 支持CORS跨域访问
- 自动处理认证和错误

## 故障排除

### 常见问题

1. **端口冲突**
   - 确保3000端口未被占用
   - 可在package.json中修改端口

2. **API连接失败**
   - 检查FastAPI是否在8000端口运行
   - 确认CORS配置正确

3. **样式不显示**
   - 检查Tailwind CSS配置
   - 确认CSS文件正确导入

4. **引用不工作**
   - 检查后端引用API端点
   - 确认引用ID格式正确

### 调试模式
开发时可以在浏览器控制台查看详细日志和错误信息。
