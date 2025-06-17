# 数据库架构说明：为什么要分三个数据库？

## 🏗️ 整体架构设计

LlamaIndex 采用了**分离关注点**的设计原则，将不同类型的数据存储在不同的数据库中，这是一种成熟的企业级架构模式。

```
┌─────────────────────────────────────────────────────────────┐
│                    LlamaIndex 存储架构                        │
├─────────────────────────────────────────────────────────────┤
│  📄 docstore.db     │  🔍 index_store.db  │  🧠 chroma.sqlite3 │
│  (文档存储)          │  (索引存储)          │  (向量存储)         │
│                    │                    │                   │
│  • 原始文档内容      │  • 索引结构配置      │  • 嵌入向量         │
│  • 文档元数据        │  • 索引映射关系      │  • 向量元数据       │
│  • 文件信息          │  • 查询配置          │  • 相似度搜索       │
│  • 文档块(chunks)    │  • 索引版本          │  • 向量集合         │
└─────────────────────────────────────────────────────────────┘
```

## 📊 三个数据库的详细职责

### 1. 📄 **docstore.db** - 文档存储数据库

**主要职责**：存储和管理文档的原始内容和元数据

**数据表结构**：
```sql
-- 文档内容表
documents (
    doc_id TEXT PRIMARY KEY,        -- 文档块ID
    doc_hash TEXT,                  -- 文档哈希
    data TEXT NOT NULL,             -- 序列化的文档内容
    file_name TEXT,                 -- 文件名
    file_size INTEGER,              -- 文件大小
    file_type TEXT,                 -- 文件类型
    chunk_index INTEGER,            -- 块索引
    created_at TIMESTAMP,           -- 创建时间
    updated_at TIMESTAMP            -- 更新时间
)

-- 文件管理表
files (
    file_id TEXT PRIMARY KEY,       -- 文件ID
    file_name TEXT UNIQUE,          -- 文件名（唯一）
    file_path TEXT,                 -- 文件路径
    file_size INTEGER,              -- 文件大小
    file_type TEXT,                 -- 文件类型
    file_hash TEXT,                 -- 文件哈希
    upload_date TIMESTAMP           -- 上传时间
)

-- 引用文档信息表
ref_doc_info (
    ref_doc_id TEXT PRIMARY KEY,    -- 引用文档ID
    node_ids TEXT,                  -- 关联的节点ID列表
    metadata TEXT                   -- 元数据
)
```

**存储内容**：
- 📝 文档的原始文本内容
- 📋 文档元数据（文件名、大小、类型等）
- 🧩 文档分块信息（每个文档被分成多个chunks）
- 🔗 文档之间的引用关系

### 2. 🔍 **index_store.db** - 索引存储数据库

**主要职责**：存储索引结构和配置信息

**数据表结构**：
```sql
-- 索引结构表
index_structs (
    index_id TEXT PRIMARY KEY,      -- 索引ID
    data TEXT NOT NULL,             -- 序列化的索引结构
    created_at TIMESTAMP,           -- 创建时间
    updated_at TIMESTAMP            -- 更新时间
)
```

**存储内容**：
- 🏗️ 索引的结构定义
- ⚙️ 索引配置参数
- 🔄 索引版本信息
- 📊 索引统计信息

### 3. 🧠 **chroma.sqlite3** - 向量存储数据库

**主要职责**：存储和管理嵌入向量，支持语义搜索

**数据表结构**（ChromaDB内部）：
```sql
-- 嵌入向量表
embeddings (
    id TEXT PRIMARY KEY,            -- 向量ID
    collection_id TEXT,             -- 集合ID
    embedding BLOB,                 -- 向量数据
    document TEXT,                  -- 关联文档
    metadata TEXT                   -- 向量元数据
)

-- 集合表
collections (
    id TEXT PRIMARY KEY,            -- 集合ID
    name TEXT,                      -- 集合名称
    metadata TEXT                   -- 集合元数据
)

-- 其他支持表...
```

**存储内容**：
- 🧠 文档的嵌入向量（高维数组）
- 🔍 向量索引结构（用于快速相似度搜索）
- 📊 向量元数据
- 🎯 向量集合管理

## 🤔 为什么要分离？

### 1. **🎯 单一职责原则**
- 每个数据库专注于一种类型的数据
- 便于维护和优化
- 降低系统复杂度

### 2. **⚡ 性能优化**
- **文档存储**：优化文本检索和存储
- **索引存储**：优化索引查询和更新
- **向量存储**：优化向量相似度计算

### 3. **🔧 技术专业化**
- **SQLite**：适合结构化数据和事务处理
- **ChromaDB**：专门为向量搜索优化

### 4. **📈 可扩展性**
- 可以独立扩展每个存储组件
- 可以替换特定的存储后端
- 支持分布式部署

### 5. **🛡️ 数据安全**
- 不同类型数据的备份策略可以不同
- 可以对敏感数据进行特殊处理
- 降低数据损坏的影响范围

## 🔄 数据流程

```
1. 文档上传
   ↓
2. 文档解析和分块 → docstore.db (存储文档内容)
   ↓
3. 生成嵌入向量 → chroma.sqlite3 (存储向量)
   ↓
4. 创建索引结构 → index_store.db (存储索引配置)
   ↓
5. 查询时：
   - 向量搜索 → chroma.sqlite3
   - 获取文档内容 → docstore.db
   - 索引配置 → index_store.db
```

## 💡 设计优势

### ✅ **优点**：
1. **模块化**：每个组件职责清晰
2. **可维护性**：便于调试和优化
3. **可替换性**：可以独立升级组件
4. **性能**：针对性优化存储和查询
5. **扩展性**：支持大规模数据处理

### ⚠️ **权衡**：
1. **复杂性**：需要管理多个数据库
2. **一致性**：需要保证数据同步
3. **事务**：跨数据库事务较复杂

## 🎯 总结

这种三数据库分离的设计是**现代RAG系统的最佳实践**：

- 📄 **docstore.db**：管理文档生命周期
- 🔍 **index_store.db**：管理索引配置
- 🧠 **chroma.sqlite3**：提供语义搜索能力

这种架构确保了系统的**高性能**、**可维护性**和**可扩展性**，是企业级RAG应用的标准设计模式。
