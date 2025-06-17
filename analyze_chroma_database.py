#!/usr/bin/env python3
"""
分析 chroma.sqlite3 数据库的完整结构
遍历所有表和字段，生成详细的说明文档
"""

import sqlite3
import os
from datetime import datetime

def analyze_chroma_database():
    """分析 ChromaDB SQLite 数据库结构"""
    print("🔍 分析 ChromaDB 数据库结构")
    print("=" * 80)
    
    chroma_db_path = "storage/chroma_db_new/chroma.sqlite3"
    
    if not os.path.exists(chroma_db_path):
        print(f"❌ 数据库文件不存在: {chroma_db_path}")
        return None
    
    # 连接数据库
    conn = sqlite3.connect(chroma_db_path)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"📊 数据库文件: {chroma_db_path}")
    print(f"📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 总表数: {len(tables)}")
    print()
    
    database_info = {
        'file_path': chroma_db_path,
        'total_tables': len(tables),
        'tables': {}
    }
    
    # 分析每个表
    for (table_name,) in tables:
        print(f"🗂️  表名: {table_name}")
        print("-" * 60)
        
        table_info = analyze_table(cursor, table_name)
        database_info['tables'][table_name] = table_info
        
        print()
    
    conn.close()
    return database_info

def analyze_table(cursor, table_name):
    """分析单个表的结构和数据"""
    table_info = {
        'columns': [],
        'indexes': [],
        'row_count': 0,
        'sample_data': []
    }
    
    try:
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("📋 字段信息:")
        for col in columns:
            cid, name, data_type, not_null, default_value, pk = col
            table_info['columns'].append({
                'name': name,
                'type': data_type,
                'not_null': bool(not_null),
                'default': default_value,
                'primary_key': bool(pk)
            })
            
            pk_indicator = " 🔑" if pk else ""
            null_indicator = " ❌" if not_null else " ✅"
            default_info = f" (默认: {default_value})" if default_value else ""
            
            print(f"  • {name}: {data_type}{pk_indicator}{null_indicator}{default_info}")
        
        # 获取索引信息
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        
        if indexes:
            print("\n🔍 索引信息:")
            for idx in indexes:
                seq, name, unique, origin, partial = idx
                unique_indicator = " 🔒" if unique else ""
                table_info['indexes'].append({
                    'name': name,
                    'unique': bool(unique),
                    'origin': origin
                })
                print(f"  • {name}{unique_indicator} ({origin})")
        
        # 获取记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        table_info['row_count'] = row_count
        print(f"\n📊 记录数: {row_count:,}")
        
        # 获取样本数据（前3条）
        if row_count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_rows = cursor.fetchall()
            table_info['sample_data'] = sample_rows
            
            print("\n📝 样本数据 (前3条):")
            column_names = [col['name'] for col in table_info['columns']]
            
            for i, row in enumerate(sample_rows, 1):
                print(f"  第{i}条:")
                for j, value in enumerate(row):
                    col_name = column_names[j] if j < len(column_names) else f"col_{j}"
                    # 截断长数据
                    if isinstance(value, str) and len(value) > 100:
                        display_value = value[:100] + "..."
                    elif isinstance(value, bytes) and len(value) > 50:
                        display_value = f"<BLOB {len(value)} bytes>"
                    else:
                        display_value = value
                    print(f"    {col_name}: {display_value}")
                print()
        
    except Exception as e:
        print(f"❌ 分析表 {table_name} 时出错: {e}")
        table_info['error'] = str(e)
    
    return table_info

def generate_markdown_report(database_info):
    """生成 Markdown 格式的分析报告"""
    
    md_content = f"""# ChromaDB 数据库结构分析报告

## 📊 基本信息

- **数据库文件**: `{database_info['file_path']}`
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **总表数**: {database_info['total_tables']}

## 📋 表结构详细说明

"""
    
    for table_name, table_info in database_info['tables'].items():
        md_content += f"""### 🗂️ 表: `{table_name}`

**记录数**: {table_info['row_count']:,}

#### 字段结构

| 字段名 | 数据类型 | 主键 | 非空 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
"""
        
        for col in table_info['columns']:
            pk_mark = "🔑" if col['primary_key'] else ""
            null_mark = "❌" if col['not_null'] else "✅"
            default_val = col['default'] if col['default'] else "-"
            
            # 根据字段名推测用途
            purpose = guess_column_purpose(table_name, col['name'], col['type'])
            
            md_content += f"| `{col['name']}` | {col['type']} | {pk_mark} | {null_mark} | {default_val} | {purpose} |\n"
        
        # 添加索引信息
        if table_info['indexes']:
            md_content += f"\n#### 索引\n\n"
            for idx in table_info['indexes']:
                unique_mark = "🔒 唯一" if idx['unique'] else "📋 普通"
                md_content += f"- **{idx['name']}**: {unique_mark} ({idx['origin']})\n"
        
        # 添加表用途说明
        table_purpose = guess_table_purpose(table_name, table_info)
        md_content += f"\n#### 表用途\n\n{table_purpose}\n\n"
        
        md_content += "---\n\n"
    
    return md_content

def guess_table_purpose(table_name, table_info):
    """根据表名和结构推测表的用途"""
    
    purposes = {
        'collections': """
**集合管理表** - 存储 ChromaDB 中的向量集合信息
- 管理不同的文档集合
- 每个集合可以有独立的配置和元数据
- 支持多租户和数据隔离
        """,
        
        'embeddings': """
**嵌入向量表** - 存储文档的向量表示
- 保存文档块的高维向量数据
- 支持语义相似度搜索
- 与文档内容建立映射关系
        """,
        
        'embedding_metadata': """
**向量元数据表** - 存储向量的附加信息
- 保存文档ID、文件名等元数据
- 支持基于元数据的过滤查询
- 建立向量与原始文档的关联
        """,
        
        'embedding_fulltext_search': """
**全文搜索表** - 支持基于关键词的文本搜索
- 提供传统的全文检索功能
- 与向量搜索形成互补
- 支持混合检索策略
        """,
        
        'segments': """
**分段管理表** - 管理数据的分段存储
- 优化大规模数据的存储和查询
- 支持数据分片和并行处理
- 提高查询性能
        """,
        
        'segment_metadata': """
**分段元数据表** - 存储分段的配置信息
- 记录分段的创建时间、大小等信息
- 支持分段的生命周期管理
- 优化存储空间使用
        """
    }
    
    return purposes.get(table_name, f"**{table_name}表** - 具体用途需要进一步分析")

def guess_column_purpose(table_name, col_name, col_type):
    """根据字段名和类型推测字段用途"""
    
    # 通用字段用途
    common_purposes = {
        'id': '唯一标识符',
        'uuid': '全局唯一标识符',
        'name': '名称',
        'metadata': '元数据信息',
        'created_at': '创建时间',
        'updated_at': '更新时间',
        'collection_id': '所属集合ID',
        'embedding': '向量数据',
        'document': '文档内容',
        'key': '键名',
        'value': '值',
        'string_value': '字符串值',
        'int_value': '整数值',
        'float_value': '浮点数值',
        'bool_value': '布尔值',
        'segment_id': '分段ID',
        'file_size': '文件大小',
        'scope': '作用域'
    }
    
    # 特定表的字段用途
    specific_purposes = {
        'collections': {
            'dimension': '向量维度',
            'tenant': '租户标识',
            'database': '数据库名称'
        },
        'embeddings': {
            'seq_id': '序列ID',
            'created_at': '向量创建时间',
            'updated_at': '向量更新时间'
        },
        'embedding_metadata': {
            'seq_id': '对应向量的序列ID'
        }
    }
    
    # 先查找特定表的字段用途
    if table_name in specific_purposes and col_name in specific_purposes[table_name]:
        return specific_purposes[table_name][col_name]
    
    # 再查找通用字段用途
    if col_name in common_purposes:
        return common_purposes[col_name]
    
    # 根据数据类型推测
    if col_type.upper() == 'BLOB':
        return '二进制数据'
    elif col_type.upper() in ['TEXT', 'VARCHAR']:
        return '文本数据'
    elif col_type.upper() in ['INTEGER', 'INT']:
        return '整数'
    elif col_type.upper() in ['REAL', 'FLOAT', 'DOUBLE']:
        return '浮点数'
    elif col_type.upper() == 'TIMESTAMP':
        return '时间戳'
    
    return '待分析'

if __name__ == "__main__":
    # 分析数据库
    database_info = analyze_chroma_database()
    
    if database_info:
        # 生成 Markdown 报告
        print("\n" + "=" * 80)
        print("📝 生成 Markdown 报告...")
        
        md_content = generate_markdown_report(database_info)
        
        # 保存报告
        report_path = "ai_records/chroma_database_structure_analysis.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ 报告已保存到: {report_path}")
        print(f"📊 分析了 {database_info['total_tables']} 个表")
