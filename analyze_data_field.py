#!/usr/bin/env python3
"""
分析 docstore.documents 表中的 data 字段
"""
import sqlite3
import json
import os

def analyze_data_field():
    """分析 data 字段的内容和结构"""
    print("🔍 分析 Documents 表的 data 字段")
    print("=" * 60)
    
    if not os.path.exists('storage/docstore.db'):
        print("❌ docstore.db 不存在")
        return
    
    conn = sqlite3.connect('storage/docstore.db')
    cursor = conn.execute('SELECT doc_id, data FROM documents LIMIT 1')
    row = cursor.fetchone()
    
    if not row:
        print("❌ 没有数据")
        conn.close()
        return
    
    doc_id, data_json = row
    print(f"📄 分析文档: {doc_id}")
    print("-" * 40)
    
    try:
        # 解析 JSON 数据
        data = json.loads(data_json)
        
        # 1. 显示数据结构概览
        print("📋 数据结构概览:")
        print(f"  总字段数: {len(data)}")
        print(f"  主要字段: {list(data.keys())}")
        
        # 2. 分析各个字段
        print("\n🔍 字段详细分析:")
        
        # ID 字段
        if 'id_' in data:
            print(f"  🆔 id_: {data['id_']}")
        
        # 类名
        if 'class_name' in data:
            print(f"  🏷️  class_name: {data['class_name']}")
        
        # 嵌入向量
        if 'embedding' in data:
            embedding = data['embedding']
            if embedding is None:
                print(f"  🧠 embedding: None (未计算)")
            else:
                print(f"  🧠 embedding: 向量长度 {len(embedding)}")
        
        # 文本内容 - 重点分析
        if 'text' in data:
            text = data['text']
            print(f"\n📝 TEXT 字段分析:")
            print(f"  类型: {type(text)}")
            print(f"  长度: {len(text)} 字符")
            
            # 检查编码问题
            text_repr = repr(text)
            if '\\u' in text_repr:
                print(f"  ⚠️  包含 Unicode 转义序列")
                print(f"  原始表示: {text_repr[:200]}...")
            else:
                print(f"  ✅ 正常的 Unicode 字符串")
            
            # 显示实际内容预览
            print(f"  内容预览: {text[:100]}...")
        
        # 元数据
        if 'metadata' in data:
            metadata = data['metadata']
            print(f"\n📁 METADATA 字段分析:")
            print(f"  字段数: {len(metadata)}")
            for key, value in metadata.items():
                if isinstance(value, str) and len(value) > 50:
                    print(f"    {key}: {value[:50]}...")
                else:
                    print(f"    {key}: {value}")
        
        # 关系字段
        if 'relationships' in data:
            relationships = data['relationships']
            print(f"\n🔗 RELATIONSHIPS 字段:")
            print(f"  关系数: {len(relationships)}")
            for rel_type, rel_data in relationships.items():
                print(f"    类型 {rel_type}: {rel_data}")
        
        # 其他字段
        other_fields = {k: v for k, v in data.items() 
                       if k not in ['id_', 'class_name', 'embedding', 'text', 'metadata', 'relationships']}
        if other_fields:
            print(f"\n🔧 其他字段:")
            for key, value in other_fields.items():
                print(f"    {key}: {value}")
        
        # 3. 计算存储开销
        print(f"\n💾 存储开销分析:")
        data_size = len(data_json)
        print(f"  JSON 总大小: {data_size} 字节")
        
        if 'text' in data:
            text_size = len(data['text'].encode('utf-8'))
            print(f"  文本内容大小: {text_size} 字节")
            print(f"  元数据开销: {data_size - text_size} 字节 ({(data_size - text_size) / data_size * 100:.1f}%)")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
    except Exception as e:
        print(f"❌ 分析失败: {e}")
    
    conn.close()

def analyze_unicode_issue():
    """专门分析 Unicode 编码问题"""
    print("\n🔤 Unicode 编码问题分析")
    print("=" * 60)
    
    conn = sqlite3.connect('storage/docstore.db')
    cursor = conn.execute('SELECT doc_id, data FROM documents LIMIT 3')
    rows = cursor.fetchall()
    
    for i, (doc_id, data_json) in enumerate(rows, 1):
        try:
            data = json.loads(data_json)
            if 'text' in data:
                text = data['text']
                print(f"\n📄 文档 {i} ({doc_id[:8]}...):")
                
                # 检查是否有中文字符
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
                print(f"  包含中文: {'是' if has_chinese else '否'}")
                
                # 检查 repr 中是否有转义序列
                text_repr = repr(text)
                has_escape = '\\u' in text_repr
                print(f"  包含转义序列: {'是' if has_escape else '否'}")
                
                # 显示前50个字符的不同表示
                preview = text[:50]
                print(f"  正常显示: {preview}")
                print(f"  repr显示: {repr(preview)}")
                
                if has_escape:
                    print(f"  ⚠️  这个文本包含 Unicode 转义，可能影响前端显示")
        
        except Exception as e:
            print(f"❌ 分析文档 {i} 失败: {e}")
    
    conn.close()

def suggest_solutions():
    """提出解决方案建议"""
    print("\n💡 解决方案建议")
    print("=" * 60)
    
    print("🎯 data 字段优化方案:")
    print("1. 保持 LlamaIndex 标准格式，确保兼容性")
    print("2. 在后端 API 中解析 data 字段，提取需要的信息")
    print("3. 前端只接收处理后的简化数据，避免复杂的 Unicode 处理")
    
    print("\n🔧 Unicode 处理方案:")
    print("1. 后端负责 Unicode 解码，确保文本正确显示")
    print("2. API 返回时使用标准 JSON 编码，避免转义序列")
    print("3. 前端接收已处理的纯文本，无需额外解码")
    
    print("\n📊 性能优化方案:")
    print("1. 缓存常用的文本内容，减少 JSON 解析开销")
    print("2. 考虑添加 text 索引，加速文本搜索")
    print("3. 分离大字段存储，减少查询时的数据传输")

def main():
    """主函数"""
    analyze_data_field()
    analyze_unicode_issue()
    suggest_solutions()

if __name__ == "__main__":
    main()
