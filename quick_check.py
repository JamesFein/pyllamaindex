#!/usr/bin/env python3
"""
快速检查数据状态
"""
import sqlite3
import os

def main():
    print("=== DOCSTORE 数据 ===")
    conn = sqlite3.connect('storage/docstore.db')
    cursor = conn.execute('SELECT doc_id, file_name, chunk_index FROM documents ORDER BY file_name, chunk_index')
    docs = cursor.fetchall()
    print(f'Documents 表记录数: {len(docs)}')
    for doc_id, file_name, chunk_index in docs:
        print(f'  {doc_id[:8]}... | {file_name} | chunk_{chunk_index}')
    conn.close()

    print('\n=== CHROMADB 数据 ===')
    chroma_file = 'storage/chroma_db_new/chroma.sqlite3'
    if os.path.exists(chroma_file):
        conn = sqlite3.connect(chroma_file)
        
        cursor = conn.execute('SELECT COUNT(*) FROM embeddings')
        embeddings_count = cursor.fetchone()[0]
        print(f'embeddings 表记录数: {embeddings_count}')
        
        cursor = conn.execute('SELECT COUNT(*) FROM embedding_metadata')
        metadata_count = cursor.fetchone()[0]
        print(f'embedding_metadata 表记录数: {metadata_count}')
        
        if metadata_count > 0:
            cursor = conn.execute("""
                SELECT id, key, string_value, int_value 
                FROM embedding_metadata 
                WHERE key IN ('file_name', 'chunk_index')
                ORDER BY id, key
            """)
            
            records = cursor.fetchall()
            print('Metadata 记录:')
            current_id = None
            for id_, key, string_value, int_value in records:
                if id_ != current_id:
                    print(f'  ID {id_}:')
                    current_id = id_
                value = string_value if string_value else int_value
                print(f'    {key}: {value}')
        
        conn.close()
    else:
        print('ChromaDB 文件不存在')

if __name__ == "__main__":
    main()
