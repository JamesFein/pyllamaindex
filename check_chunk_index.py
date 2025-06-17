#!/usr/bin/env python3
"""
检查 chunk_index 的问题
"""
import sqlite3
import json

def check_chunk_index_issue():
    """检查 chunk_index 的分布和问题"""
    print("🔍 检查 Documents 表中的 chunk_index 问题")
    print("=" * 60)
    
    with sqlite3.connect('storage/docstore.db') as conn:
        # 1. 检查 chunk_index 分布
        cursor = conn.execute('''
            SELECT file_name, chunk_index, COUNT(*) as count
            FROM documents 
            GROUP BY file_name, chunk_index 
            ORDER BY file_name, chunk_index
        ''')
        
        print("📊 chunk_index 分布:")
        print("文件名                | 块索引 | 数量")
        print("-" * 50)
        
        chunk_data = {}
        for row in cursor.fetchall():
            file_name, chunk_index, count = row
            print(f"{file_name:<20} | {chunk_index:<6} | {count}")
            
            if file_name not in chunk_data:
                chunk_data[file_name] = []
            chunk_data[file_name].append((chunk_index, count))
        
        # 2. 分析问题
        print(f"\n🔍 问题分析:")
        
        total_docs = 0
        files_with_issue = 0
        
        for file_name, chunks in chunk_data.items():
            total_chunks = sum(count for _, count in chunks)
            total_docs += total_chunks
            
            # 检查是否所有块的索引都是0
            all_zero = all(chunk_index == 0 for chunk_index, _ in chunks)
            
            if all_zero and total_chunks > 1:
                files_with_issue += 1
                print(f"⚠️  {file_name}: {total_chunks} 个块，但 chunk_index 都是 0")
            elif not all_zero:
                print(f"✅ {file_name}: chunk_index 正常分布")
            else:
                print(f"ℹ️  {file_name}: 只有 1 个块，chunk_index=0 正常")
        
        print(f"\n📈 统计:")
        print(f"总文档块数: {total_docs}")
        print(f"有问题的文件数: {files_with_issue}")
        
        # 3. 检查具体内容
        print(f"\n📄 检查文档内容长度:")
        cursor = conn.execute('''
            SELECT file_name, chunk_index, LENGTH(data) as data_length,
                   doc_id
            FROM documents 
            ORDER BY file_name, chunk_index
        ''')
        
        for row in cursor.fetchall():
            file_name, chunk_index, data_length, doc_id = row
            print(f"{file_name:<20} | 块{chunk_index} | {data_length:>6} 字符 | {doc_id[:20]}...")

def analyze_chunking_logic():
    """分析分块逻辑的问题"""
    print(f"\n🔍 分析分块逻辑问题")
    print("=" * 60)
    
    print("📋 可能的原因:")
    print("1. generate.py 中的 chunk_index 计算逻辑有误")
    print("2. 每次运行 generate 都重新生成 node_id，导致重复")
    print("3. 文档分块器可能没有正确分块")
    print("4. chunk_index 赋值逻辑错误")
    
    print(f"\n🎯 正确的 chunk_index 应该是:")
    print("- 同一个文件的不同块应该有不同的 chunk_index")
    print("- 第一个块: chunk_index = 0")
    print("- 第二个块: chunk_index = 1")
    print("- 第三个块: chunk_index = 2")
    print("- ...")
    
    print(f"\n⚠️  当前问题的影响:")
    print("1. 无法正确识别文档块的顺序")
    print("2. 可能影响文档重建和显示")
    print("3. 引用时无法准确定位到具体段落")
    print("4. 可能导致搜索结果混乱")

def check_generate_logic():
    """检查 generate.py 中的逻辑"""
    print(f"\n🔍 检查 generate.py 中的分块逻辑")
    print("=" * 60)
    
    try:
        with open('generate.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找 chunk_index 相关的代码
        lines = content.split('\n')
        chunk_index_lines = []
        
        for i, line in enumerate(lines):
            if 'chunk_index' in line.lower():
                chunk_index_lines.append((i+1, line.strip()))
        
        if chunk_index_lines:
            print("📄 generate.py 中的 chunk_index 相关代码:")
            for line_num, line in chunk_index_lines:
                print(f"第{line_num}行: {line}")
        else:
            print("❌ 在 generate.py 中没有找到 chunk_index 相关代码")
            
    except Exception as e:
        print(f"❌ 读取 generate.py 失败: {e}")

def suggest_fixes():
    """建议修复方案"""
    print(f"\n💡 修复建议")
    print("=" * 60)
    
    print("🔧 方案1: 修复 generate.py 中的 chunk_index 逻辑")
    print("- 确保为同一文件的不同块分配递增的 chunk_index")
    print("- 修改循环逻辑，正确计算块索引")
    
    print(f"\n🔧 方案2: 重新生成索引")
    print("- 先重置数据库")
    print("- 修复代码后重新运行 generate")
    
    print(f"\n🔧 方案3: 数据库修复脚本")
    print("- 创建脚本重新计算 chunk_index")
    print("- 基于文档内容和顺序重新分配索引")

def main():
    """主检查流程"""
    check_chunk_index_issue()
    analyze_chunking_logic()
    check_generate_logic()
    suggest_fixes()

if __name__ == "__main__":
    main()
