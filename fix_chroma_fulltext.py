#!/usr/bin/env python3
"""
修复 ChromaDB embedding_fulltext_search 表结构问题
"""
import os
import sqlite3
import shutil

def fix_chroma_fulltext_search():
    """修复 ChromaDB 的 embedding_fulltext_search 表结构"""
    print("🔧 修复 ChromaDB embedding_fulltext_search 表结构")
    print("=" * 60)
    
    chroma_db_path = "storage/chroma_db_new"
    
    if not os.path.exists(chroma_db_path):
        print("❌ ChromaDB 目录不存在")
        return False
    
    # 查找 ChromaDB 的 SQLite 数据库文件
    chroma_db_file = None
    for file in os.listdir(chroma_db_path):
        if file.endswith('.sqlite3'):
            chroma_db_file = os.path.join(chroma_db_path, file)
            break
    
    if not chroma_db_file:
        print("❌ 没有找到 ChromaDB SQLite 文件")
        return False
    
    print(f"📄 找到 ChromaDB 文件: {chroma_db_file}")
    
    try:
        # 备份原文件
        backup_file = chroma_db_file + ".backup"
        shutil.copy2(chroma_db_file, backup_file)
        print(f"✅ 创建备份: {backup_file}")
        
        # 连接数据库
        conn = sqlite3.connect(chroma_db_file)
        cursor = conn.cursor()
        
        # 检查现有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 现有表: {tables}")
        
        # 检查是否存在 embedding_fulltext_search 表
        if 'embedding_fulltext_search' in tables:
            print("⚠️  发现损坏的 embedding_fulltext_search 表，尝试修复...")
            
            # 删除损坏的表
            try:
                cursor.execute("DROP TABLE IF EXISTS embedding_fulltext_search")
                print("✅ 删除损坏的 embedding_fulltext_search 表")
            except Exception as e:
                print(f"⚠️  删除表时出错: {e}")
        
        # 重新创建 embedding_fulltext_search 表
        try:
            # 这是 ChromaDB 的标准 FTS 表结构
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS embedding_fulltext_search 
                USING fts5(
                    document, 
                    content='embeddings', 
                    content_rowid='rowid'
                )
            """)
            print("✅ 重新创建 embedding_fulltext_search 表")
            
            # 提交更改
            conn.commit()
            print("✅ 数据库修复完成")
            
        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            # 恢复备份
            conn.close()
            shutil.copy2(backup_file, chroma_db_file)
            print("✅ 已恢复备份")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def test_chroma_after_fix():
    """测试修复后的 ChromaDB"""
    print("\n🧪 测试修复后的 ChromaDB")
    print("=" * 60)
    
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
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
        print(f"✅ ChromaDB 连接成功，向量数: {count}")
        
        # 测试查询
        if count > 0:
            result = collection.get(limit=1)
            if result['ids']:
                print("✅ 数据查询正常")
            else:
                print("⚠️  数据查询异常")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB 测试失败: {e}")
        return False

def clean_duplicate_data():
    """清理重复数据"""
    print("\n🧹 清理重复数据")
    print("=" * 60)
    
    try:
        import sqlite3
        
        # 清理 docstore 中的重复数据
        docstore_path = "storage/docstore.db"
        if os.path.exists(docstore_path):
            conn = sqlite3.connect(docstore_path)
            
            # 检查重复文件
            cursor = conn.execute("""
                SELECT file_name, COUNT(*) as count 
                FROM documents 
                WHERE file_name IS NOT NULL 
                GROUP BY file_name 
                HAVING count > 1
            """)
            
            duplicates = cursor.fetchall()
            if duplicates:
                print("发现重复文件:")
                for file_name, count in duplicates:
                    print(f"  {file_name}: {count} 条记录")
                
                print("建议重新运行 generate.py 来清理重复数据")
            else:
                print("✅ 没有发现重复数据")
            
            conn.close()
        
    except Exception as e:
        print(f"❌ 清理重复数据失败: {e}")

def main():
    """主函数"""
    print("🔧 ChromaDB embedding_fulltext_search 修复工具")
    print("=" * 80)
    
    # 1. 修复 embedding_fulltext_search 表
    if fix_chroma_fulltext_search():
        print("\n✅ embedding_fulltext_search 表修复成功")
        
        # 2. 测试修复结果
        if test_chroma_after_fix():
            print("\n✅ ChromaDB 修复验证通过")
        else:
            print("\n❌ ChromaDB 修复验证失败")
    else:
        print("\n❌ embedding_fulltext_search 表修复失败")
    
    # 3. 清理重复数据
    clean_duplicate_data()
    
    print("\n💡 修复完成！")
    print("如果仍有问题，建议:")
    print("1. 重新运行 uv run generate 来重新生成索引")
    print("2. 检查 ChromaDB 错误日志")

if __name__ == "__main__":
    main()
