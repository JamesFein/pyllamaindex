#!/usr/bin/env python3
"""
清理数据库并测试修复
"""
import os
import shutil
from app.storage_config import get_storage_context
from app.index import STORAGE_DIR

def clear_all_data():
    """清理所有数据"""
    print("🧹 清理所有数据")
    print("=" * 60)

    print("⚠️  请先停止服务器，然后手动删除以下目录和文件:")
    print(f"1. 删除存储目录: {STORAGE_DIR}")
    print("2. 删除 data 目录中的所有文件")
    print("3. 然后重新运行此脚本")

    # 检查是否已清理
    if os.path.exists(STORAGE_DIR):
        print(f"❌ 存储目录仍然存在: {STORAGE_DIR}")
        return False

    print("✅ 存储目录已清理")
    return True

def create_test_files():
    """创建测试文件"""
    print("\n📝 创建测试文件")
    print("=" * 60)
    
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # 创建测试文件1
    test_file1 = os.path.join(data_dir, "test1.txt")
    with open(test_file1, "w", encoding="utf-8") as f:
        f.write("""第一个测试文档

这是第一个测试文档的内容。它包含多个段落，用于测试文档分块功能。

## 第一部分
这是第一部分的内容。我们需要确保每个文本块都有正确的索引号。

## 第二部分  
这是第二部分的内容。chunk_index 应该从1开始递增。

## 第三部分
这是第三部分的内容。让我们看看分块是否正确工作。""")
    
    print(f"✅ 创建测试文件: {test_file1}")
    
    # 创建测试文件2
    test_file2 = os.path.join(data_dir, "test2.txt")
    with open(test_file2, "w", encoding="utf-8") as f:
        f.write("""第二个测试文档

这是第二个测试文档，用于测试同名文件处理。

内容比较短，应该只分成少数几个块。""")
    
    print(f"✅ 创建测试文件: {test_file2}")

def test_upload_and_check():
    """测试上传并检查结果"""
    print("\n🧪 测试上传并检查结果")
    print("=" * 60)
    
    # 这里我们需要手动上传文件，因为我们在脚本中
    print("请通过以下步骤测试:")
    print("1. 启动服务器: uv fastapi run dev")
    print("2. 上传 data/test1.txt 文件")
    print("3. 上传 data/test2.txt 文件")
    print("4. 运行 python test_storage_fixes.py 检查结果")
    print("5. 再次上传 test1.txt (测试同名文件处理)")
    print("6. 再次运行测试脚本检查结果")

def main():
    """主函数"""
    print("🧪 清理数据库并测试修复")
    print("=" * 80)

    if clear_all_data():
        create_test_files()
        test_upload_and_check()
    else:
        print("\n请先清理数据，然后重新运行脚本")

if __name__ == "__main__":
    main()
