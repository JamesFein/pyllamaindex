#!/usr/bin/env python3
"""
测试优化后的存储配置
"""
import os
import logging
from app.storage_config import get_storage_context, load_storage_context

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_storage_creation():
    """测试存储上下文创建"""
    logger.info("🧪 测试存储上下文创建...")
    
    try:
        storage_context = get_storage_context("storage")
        
        # 检查组件
        logger.info(f"✅ Vector Store: {type(storage_context.vector_store).__name__}")
        logger.info(f"✅ Document Store: {type(storage_context.docstore).__name__}")
        logger.info(f"✅ Index Store: {type(storage_context.index_store).__name__}")
        
        # 检查是否禁用了不需要的组件
        if hasattr(storage_context, 'graph_store') and storage_context.graph_store is None:
            logger.info("✅ Graph Store: 已禁用")
        else:
            logger.warning("⚠️  Graph Store: 未正确禁用")
        
        if hasattr(storage_context, 'image_store') and storage_context.image_store is None:
            logger.info("✅ Image Store: 已禁用")
        else:
            logger.warning("⚠️  Image Store: 未正确禁用")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 存储上下文创建失败: {e}")
        return False

def test_storage_loading():
    """测试存储上下文加载"""
    logger.info("🧪 测试存储上下文加载...")
    
    try:
        storage_context = load_storage_context("storage")
        
        if storage_context:
            logger.info("✅ 存储上下文加载成功")
            return True
        else:
            logger.warning("⚠️  存储上下文加载返回None")
            return False
            
    except Exception as e:
        logger.error(f"❌ 存储上下文加载失败: {e}")
        return False

def check_storage_files():
    """检查存储文件状态"""
    logger.info("🧪 检查存储文件...")
    
    storage_dir = "storage"
    required_files = [
        "docstore.db",
        "index_store.db",
        "chroma_db"
    ]
    
    unwanted_files = [
        "graph_store.json",
        "image__vector_store.json"
    ]
    
    # 检查必需文件
    all_required_exist = True
    for file_name in required_files:
        file_path = os.path.join(storage_dir, file_name)
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                logger.info(f"✅ {file_name}: {size:,} bytes")
            else:
                logger.info(f"✅ {file_name}: 目录存在")
        else:
            logger.error(f"❌ {file_name}: 不存在")
            all_required_exist = False
    
    # 检查不需要的文件
    no_unwanted_files = True
    for file_name in unwanted_files:
        file_path = os.path.join(storage_dir, file_name)
        if os.path.exists(file_path):
            logger.warning(f"⚠️  {file_name}: 不应该存在")
            no_unwanted_files = False
        else:
            logger.info(f"✅ {file_name}: 正确地不存在")
    
    return all_required_exist and no_unwanted_files

def main():
    """主测试流程"""
    print("🧪 存储配置测试")
    print("=" * 40)
    
    tests = [
        ("存储上下文创建", test_storage_creation),
        ("存储上下文加载", test_storage_loading),
        ("存储文件检查", check_storage_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            print(f"✅ {test_name} - 通过")
            passed += 1
        else:
            print(f"❌ {test_name} - 失败")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！存储配置优化成功")
    else:
        print("⚠️  部分测试失败，需要检查配置")

if __name__ == "__main__":
    main()
