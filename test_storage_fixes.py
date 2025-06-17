#!/usr/bin/env python3
"""
测试存储逻辑修复
"""
import os
import sqlite3
import json
import chromadb
from chromadb.config import Settings as ChromaSettings

def test_chunk_index_fix():
    """测试 chunk_index 修复"""
    print("🔧 测试 chunk_index 修复")
    print("=" * 60)
    
    if not os.path.exists('storage/docstore.db'):
        print("❌ docstore.db 不存在，请先上传一些文档")
        return
    
    conn = sqlite3.connect('storage/docstore.db')
    
    # 检查 chunk_index 分布
    cursor = conn.execute("""
        SELECT file_name, chunk_index, COUNT(*) as count
        FROM documents 
        WHERE file_name IS NOT NULL 
        GROUP BY file_name, chunk_index 
        ORDER BY file_name, chunk_index
    """)
    
    results = cursor.fetchall()
    print("📊 Chunk_index 分布:")
    
    current_file = None
    for file_name, chunk_index, count in results:
        if file_name != current_file:
            print(f"\n📄 {file_name}:")
            current_file = file_name
        print(f"  chunk_index={chunk_index}: {count} 条记录")
    
    # 检查是否还有 chunk_index = 0 的问题
    cursor = conn.execute("SELECT COUNT(*) FROM documents WHERE chunk_index = 0")
    zero_count = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) FROM documents WHERE chunk_index > 0")
    positive_count = cursor.fetchone()[0]
    
    print(f"\n📈 统计:")
    print(f"  chunk_index = 0: {zero_count} 条记录")
    print(f"  chunk_index > 0: {positive_count} 条记录")
    
    if zero_count > 0 and positive_count == 0:
        print("  ⚠️  仍然存在 chunk_index = 0 的问题")
    elif positive_count > 0:
        print("  ✅ chunk_index 修复成功")
    
    conn.close()

def test_same_file_handling():
    """测试同名文件处理"""
    print("\n🔄 测试同名文件处理")
    print("=" * 60)
    
    if not os.path.exists('storage/docstore.db'):
        print("❌ docstore.db 不存在")
        return
    
    conn = sqlite3.connect('storage/docstore.db')
    
    # 检查文件重复情况
    cursor = conn.execute("""
        SELECT file_name, COUNT(*) as count
        FROM documents 
        WHERE file_name IS NOT NULL 
        GROUP BY file_name
        ORDER BY count DESC, file_name
    """)
    
    results = cursor.fetchall()
    print("📁 文件重复情况:")
    
    has_duplicates = False
    for file_name, count in results:
        if count > 1:
            print(f"  ⚠️  {file_name}: {count} 条记录 (重复)")
            has_duplicates = True
        else:
            print(f"  ✅ {file_name}: {count} 条记录")
    
    if not has_duplicates:
        print("  ✅ 没有发现重复文件")
    
    conn.close()

def test_chroma_consistency():
    """测试 ChromaDB 一致性"""
    print("\n🧠 测试 ChromaDB 一致性")
    print("=" * 60)
    
    # 获取 docstore 中的 doc_id
    docstore_ids = set()
    if os.path.exists('storage/docstore.db'):
        conn = sqlite3.connect('storage/docstore.db')
        cursor = conn.execute("SELECT doc_id FROM documents")
        docstore_ids = {row[0] for row in cursor.fetchall()}
        conn.close()
        print(f"📄 Docstore 中的文档数: {len(docstore_ids)}")
    
    # 获取 chroma 中的 ID
    chroma_ids = set()
    chroma_path = 'storage/chroma_db_new'
    if os.path.exists(chroma_path):
        try:
            client = chromadb.PersistentClient(
                path=chroma_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            collection = client.get_collection('document_vectors')
            result = collection.get()
            chroma_ids = set(result['ids'])
            print(f"🧠 ChromaDB 中的向量数: {len(chroma_ids)}")
        except Exception as e:
            print(f"❌ 无法访问 ChromaDB: {e}")
            return
    
    # 比较一致性
    if docstore_ids and chroma_ids:
        common_ids = docstore_ids & chroma_ids
        docstore_only = docstore_ids - chroma_ids
        chroma_only = chroma_ids - docstore_ids
        
        print(f"🔗 数据一致性:")
        print(f"  共同 ID: {len(common_ids)}")
        print(f"  仅在 Docstore: {len(docstore_only)}")
        print(f"  仅在 ChromaDB: {len(chroma_only)}")
        
        if len(docstore_only) == 0 and len(chroma_only) == 0:
            print("  ✅ 数据完全一致")
        else:
            print("  ⚠️  数据不一致")
            if docstore_only:
                print(f"    Docstore 独有 (前3个): {list(docstore_only)[:3]}")
            if chroma_only:
                print(f"    ChromaDB 独有 (前3个): {list(chroma_only)[:3]}")

def test_data_field_structure():
    """测试 data 字段结构"""
    print("\n📋 测试 data 字段结构")
    print("=" * 60)
    
    if not os.path.exists('storage/docstore.db'):
        print("❌ docstore.db 不存在")
        return
    
    conn = sqlite3.connect('storage/docstore.db')
    cursor = conn.execute('SELECT doc_id, data FROM documents LIMIT 1')
    row = cursor.fetchone()
    
    if row:
        doc_id, data_json = row
        try:
            data = json.loads(data_json)
            
            # 检查关键字段
            print(f"📄 文档 {doc_id[:8]}... 的 data 字段:")
            print(f"  包含 text: {'text' in data}")
            print(f"  包含 metadata: {'metadata' in data}")
            
            if 'metadata' in data:
                metadata = data['metadata']
                print(f"  metadata 中的 chunk_index: {metadata.get('chunk_index', 'None')}")
                print(f"  metadata 中的 file_name: {metadata.get('file_name', 'None')}")
            
            if 'text' in data:
                text_length = len(data['text'])
                print(f"  text 长度: {text_length} 字符")
                print(f"  text 预览: {data['text'][:50]}...")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
    else:
        print("❌ 没有数据")
    
    conn.close()

def main():
    """主函数"""
    print("🧪 存储逻辑修复测试")
    print("=" * 80)
    
    test_chunk_index_fix()
    test_same_file_handling()
    test_chroma_consistency()
    test_data_field_structure()
    
    print("\n💡 测试完成")
    print("如果发现问题，请检查修复是否正确应用")

if __name__ == "__main__":
    main()
