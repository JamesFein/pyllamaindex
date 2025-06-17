🧩 1. id*：唯一标识符
json
Copy
Edit
"id*": "50819b44-34d8-49c1-9724-3351f08cc076"
这个字段是该文本块（TextNode）的全局唯一 ID。

📦 2. embedding：嵌入向量
json
Copy
Edit
"embedding": null
此处为 null，说明该文本块 尚未完成嵌入计算（即还没有计算向量，未入库至 Chroma）。

📁 3. metadata：元信息
记录该文本块来自哪个文件，以及文件的一些属性：

json
Copy
Edit
"file_path": "D:\\create-lllama\\pyllamaindex\\data\\product_info.txt",
"file_name": "product_info.txt",
"file_type": "text/plain",
"file_size": 1236,
"creation_date": "2025-06-17",
"last_modified_date": "2025-06-17",
"file_id": "file_4a5dbd61",
"chunk_index": 0
解释：

字段 含义
file_path 文件绝对路径
file_name 文件名
file_type MIME 类型
file_size 文件大小（字节）
chunk_index 本 chunk 在原文档中的序号
file_id 文件的唯一标识符

🔕 4. excluded_embed_metadata_keys & excluded_llm_metadata_keys
json
Copy
Edit
"excluded_embed_metadata_keys": ["file_name", "file_type", ...]
这些字段 不会被包含到嵌入向量或 LLM 提示中，避免噪声影响向量计算或大模型生成。

🔗 5. relationships
json
Copy
Edit
"relationships": {
"1": {
"node_id": "...",
"node_type": "4",
...
}
}
这表示该文本块与另一个节点（比如文件级别的节点）存在关联，便于文档结构建模。

📝 6. text：文本内容（已转码为 Unicode）
json
Copy
Edit
"text": "产品信息\n\n## AI 智能助手\n\n 我们..."
这是最重要的字段，内容为：

产品信息简略预览（原始 Unicode 已解码）：
markdown
Copy
Edit
产品信息

## AI 智能助手

我们的旗舰产品是 AI 智能助手，它集成了最新的人工智能技术，能够为用户提供全方位的智能服务。

### 核心功能

1. 智能对话（自然语言理解、上下文记忆、多轮对话支持）
2. 知识问答（海量知识库、精准答案匹配、实时信息更新）
3. 任务执行（日程管理、邮件处理、文档生成）

### 技术特点

- 高准确率：采用先进的深度学习模型，问答准确率达 95%以上
- 快速响应：优化的算法结构，平均响应时间小于 1 秒
- 多语言支持：支持中、英、日等多种语言
- 个性化定制：根据用户习惯进行个性化调优

### 应用场景

1. 企业办公（会议记录、报告生成、数据分析辅助）
2. 客户服务（24 小时在线客服、FAQ 解答、投诉处理协助）
3. 教育培训（在线答疑、学习计划制定、知识点讲解）

### 价格方案

- 基础版：免费，包含基本对话功能
- 专业版：99 元/月，包含高级功能和 API 接口
- 企业版：999 元/月，包含定制化服务和技术支持
  🧱 7. 其它结构字段
  "start_char_idx": 0 和 "end_char_idx": 597：文本在原文中的字符起止位置。

"class_name": "TextNode"：表示这是一个“文本节点”。

✅ 总结：这个数据结构的作用
这是一个典型的 用于知识检索系统的文本块对象，包含了：

文本内容（text）

元信息（metadata）

关系（relationships）

嵌入向量（embedding，当前为 null）
