#!/usr/bin/env python3
"""
诊断 embedding_metadata 数据不完整的问题
"""
import sqlite3
import os
import chromadb
from chromadb.config import Settings as ChromaSettings

def check_docstore_data():
    """检查 docstore 中的数据"""
    print("📄 检查 Docstore 数据")
    print("=" * 60)
    
    if not os.path.exists('storage/docstore.db'):
        print("❌ docstore.db 不存在")
        return []
    
    conn = sqlite3.connect('storage/docstore.db')
    
    # 检查 documents 表
    cursor = conn.execute("""
        SELECT doc_id, file_name, chunk_index, LENGTH(data) as data_size
        FROM documents 
        ORDER BY file_name, chunk_index
    """)
    
    docs = cursor.fetchall()
    print(f"📊 Documents 表记录数: {len(docs)}")
    
    doc_ids = []
    for doc_id, file_name, chunk_index, data_size in docs:
        print(f"  {doc_id[:8]}... | {file_name} | chunk_{chunk_index} | {data_size}B")
        doc_ids.append(doc_id)
    
    conn.close()
    return doc_ids

def check_chroma_data():
    """检查 ChromaDB 中的数据"""
    print("\n🧠 检查 ChromaDB 数据")
    print("=" * 60)
    
    try:
        chroma_path = 'storage/chroma_db_new'
        client = chromadb.PersistentClient(
            path=chroma_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        collection = client.get_collection('document_vectors')
        count = collection.count()
        print(f"📊 ChromaDB 向量总数: {count}")
        
        if count > 0:
            # 获取所有数据
            result = collection.get()
            print(f"📋 实际获取到的记录数: {len(result['ids'])}")
            
            chroma_ids = []
            for i, (id_, metadata) in enumerate(zip(result['ids'], result['metadatas'] or [])):
                file_name = metadata.get('file_name', 'Unknown') if metadata else 'No metadata'
                chunk_index = metadata.get('chunk_index', 'Unknown') if metadata else 'No metadata'
                print(f"  {id_[:8]}... | {file_name} | chunk_{chunk_index}")
                chroma_ids.append(id_)
            
            return chroma_ids
        else:
            print("❌ ChromaDB 中没有数据")
            return []
            
    except Exception as e:
        print(f"❌ ChromaDB 检查失败: {e}")
        return []

def check_chroma_sqlite():
    """检查 ChromaDB 的 SQLite 文件"""
    print("\n🗄️ 检查 ChromaDB SQLite 文件")
    print("=" * 60)
    
    chroma_db_path = "storage/chroma_db_new"
    chroma_db_file = None
    
    for file in os.listdir(chroma_db_path):
        if file.endswith('.sqlite3'):
            chroma_db_file = os.path.join(chroma_db_path, file)
            break
    
    if not chroma_db_file:
        print("❌ 没有找到 ChromaDB SQLite 文件")
        return
    
    print(f"📄 ChromaDB 文件: {chroma_db_file}")
    
    try:
        conn = sqlite3.connect(chroma_db_file)
        
        # 检查 embeddings 表
        cursor = conn.execute("SELECT COUNT(*) FROM embeddings")
        embeddings_count = cursor.fetchone()[0]
        print(f"📊 embeddings 表记录数: {embeddings_count}")
        
        # 检查 embedding_metadata 表
        cursor = conn.execute("SELECT COUNT(*) FROM embedding_metadata")
        metadata_count = cursor.fetchone()[0]
        print(f"📊 embedding_metadata 表记录数: {metadata_count}")
        
        # 检查具体的 metadata 记录
        if metadata_count > 0:
            cursor = conn.execute("""
                SELECT id, key, string_value, int_value 
                FROM embedding_metadata 
                WHERE key IN ('file_name', 'chunk_index')
                ORDER BY id, key
            """)
            
            metadata_records = cursor.fetchall()
            print(f"📋 Metadata 记录详情:")
            
            current_id = None
            for id_, key, string_value, int_value in metadata_records:
                if id_ != current_id:
                    print(f"\n  ID {id_}:")
                    current_id = id_
                
                value = string_value if string_value else int_value
                print(f"    {key}: {value}")
        
        # 检查 embedding_fulltext_search 表状态
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM embedding_fulltext_search")
            fts_count = cursor.fetchone()[0]
            print(f"📊 embedding_fulltext_search 表记录数: {fts_count}")
        except Exception as e:
            print(f"⚠️  embedding_fulltext_search 表问题: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查 ChromaDB SQLite 失败: {e}")

def compare_data_consistency():
    """比较数据一致性"""
    print("\n🔗 比较数据一致性")
    print("=" * 60)
    
    docstore_ids = check_docstore_data()
    chroma_ids = check_chroma_data()
    
    if docstore_ids and chroma_ids:
        docstore_set = set(docstore_ids)
        chroma_set = set(chroma_ids)
        
        common = docstore_set & chroma_set
        docstore_only = docstore_set - chroma_set
        chroma_only = chroma_set - docstore_set
        
        print(f"\n📊 数据一致性分析:")
        print(f"  Docstore 总数: {len(docstore_ids)}")
        print(f"  ChromaDB 总数: {len(chroma_ids)}")
        print(f"  共同 ID 数: {len(common)}")
        print(f"  仅在 Docstore: {len(docstore_only)}")
        print(f"  仅在 ChromaDB: {len(chroma_only)}")
        
        if docstore_only:
            print(f"\n❌ 缺失的向量 (在 Docstore 但不在 ChromaDB):")
            for doc_id in list(docstore_only)[:5]:  # 只显示前5个
                print(f"    {doc_id}")
        
        if chroma_only:
            print(f"\n⚠️  孤立的向量 (在 ChromaDB 但不在 Docstore):")
            for doc_id in list(chroma_only)[:5]:  # 只显示前5个
                print(f"    {doc_id}")

def suggest_fixes():
    """建议修复方案"""
    print("\n💡 修复建议")
    print("=" * 60)
    
    print("基于诊断结果，可能的问题和解决方案:")
    print()
    print("1. **向量索引创建失败**")
    print("   - 原因: VectorStoreIndex 创建过程中出现异常")
    print("   - 解决: 检查 OpenAI API 连接和配额")
    print()
    print("2. **ChromaDB 批量插入问题**")
    print("   - 原因: 批量插入时部分数据失败")
    print("   - 解决: 改为逐个插入或检查数据格式")
    print()
    print("3. **embedding_fulltext_search 表问题**")
    print("   - 原因: FTS 表损坏影响插入")
    print("   - 解决: 重新修复 FTS 表或禁用全文搜索")
    print()
    print("4. **数据重复或冲突**")
    print("   - 原因: 相同 ID 的数据重复插入")
    print("   - 解决: 清理重复数据后重新生成")

def main():
    """主函数"""
    print("🔍 Embedding Metadata 数据不完整诊断")
    print("=" * 80)
    
    check_docstore_data()
    check_chroma_data()
    check_chroma_sqlite()
    compare_data_consistency()
    suggest_fixes()

if __name__ == "__main__":
    main()
