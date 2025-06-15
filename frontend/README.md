# AI聊天前端

这是一个基于HTML、CSS和JavaScript构建的AI聊天界面，用于与FastAPI后端进行交互。

## 功能特性

- 🎨 现代化的聊天界面设计
- 📁 文件上传功能（支持PDF、TXT、DOC、DOCX）
- 💬 实时聊天对话
- 📱 响应式设计，支持移动端
- ⚡ 实时字符计数
- 🔄 加载状态指示
- 📎 文件管理（上传、显示、删除）

## 文件结构

```
frontend/
├── index.html      # 主页面
├── style.css       # 样式文件
├── script.js       # JavaScript逻辑
└── README.md       # 说明文档
```

## API集成

前端与以下API端点进行交互：

### 1. 聊天API
- **端点**: `POST /api/chat`
- **功能**: 发送消息并获取AI回复
- **请求格式**: 
```json
{
  "id": "chat_id",
  "messages": [
    {
      "role": "user",
      "content": "用户消息",
      "annotations": [...]
    }
  ],
  "data": {}
}
```

### 2. 文件上传API
- **端点**: `POST /api/chat/file`
- **功能**: 上传文件并获取文件ID
- **请求格式**:
```json
{
  "name": "文件名",
  "base64": "base64编码的文件内容",
  "params": "文件参数JSON字符串"
}
```

## 使用方法

1. 启动FastAPI服务器
2. 访问根路径 `/` 即可看到聊天界面
3. 在输入框中输入消息并发送
4. 可以通过点击📎按钮上传文件
5. 上传的文件会在消息中作为附件发送给AI

## 技术特点

- 使用原生JavaScript，无需额外框架
- CSS Grid和Flexbox布局
- 异步文件上传和API调用
- 自动文本区域大小调整
- 平滑的动画效果
- 错误处理和用户反馈

## 浏览器兼容性

支持所有现代浏览器：
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+
