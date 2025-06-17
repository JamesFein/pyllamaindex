#!/usr/bin/env python3
"""
调试索引加载问题
"""
import os
import logging
from dotenv import load_dotenv

# 设置详细的日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_step_by_step():
    """逐步测试索引加载过程"""
    print("🔍 逐步调试索引加载")
    print("=" * 60)
    
    # 1. 加载环境变量
    print("1. 加载环境变量...")
    load_dotenv()
    print("✅ 环境变量加载完成")
    
    # 2. 初始化设置
    print("\n2. 初始化设置...")
    try:
        from app.settings import init_settings
        init_settings()
        print("✅ 设置初始化完成")
    except Exception as e:
        print(f"❌ 设置初始化失败: {e}")
        return False
    
    # 3. 检查存储目录
    print("\n3. 检查存储目录...")
    STORAGE_DIR = "storage"
    if os.path.exists(STORAGE_DIR):
        print(f"✅ 存储目录存在: {STORAGE_DIR}")
        files = os.listdir(STORAGE_DIR)
        print(f"📁 目录内容: {files}")
    else:
        print(f"❌ 存储目录不存在: {STORAGE_DIR}")
        return False
    
    # 4. 测试存储上下文加载
    print("\n4. 测试存储上下文加载...")
    try:
        from app.storage_config import load_storage_context
        storage_context = load_storage_context(STORAGE_DIR)
        if storage_context:
            print("✅ 存储上下文加载成功")
            print(f"📄 Docstore 类型: {type(storage_context.docstore)}")
            print(f"🧠 Vector store 类型: {type(storage_context.vector_store)}")
            print(f"📚 Index store 类型: {type(storage_context.index_store)}")
        else:
            print("❌ 存储上下文加载失败")
            return False
    except Exception as e:
        print(f"❌ 存储上下文加载异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. 测试向量存储连接
    print("\n5. 测试向量存储连接...")
    try:
        # 检查 ChromaDB 集合
        vector_store = storage_context.vector_store
        if hasattr(vector_store, '_collection'):
            collection = vector_store._collection
            count = collection.count()
            print(f"✅ ChromaDB 连接成功，向量数: {count}")
        else:
            print("⚠️  无法访问 ChromaDB 集合")
    except Exception as e:
        print(f"❌ 向量存储连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. 测试索引创建
    print("\n6. 测试索引创建...")
    try:
        from llama_index.core.indices import VectorStoreIndex
        
        print("  6.1 尝试从向量存储创建索引...")
        index = VectorStoreIndex.from_vector_store(
            storage_context.vector_store,
            storage_context=storage_context
        )
        print("✅ 索引创建成功")
        print(f"📊 索引类型: {type(index)}")
        
        # 测试查询引擎
        print("  6.2 测试查询引擎创建...")
        query_engine = index.as_query_engine(similarity_top_k=1)
        print("✅ 查询引擎创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 索引创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_index_function():
    """测试 get_index 函数"""
    print("\n🎯 测试 get_index 函数")
    print("=" * 60)
    
    try:
        from app.index import get_index
        
        print("调用 get_index()...")
        index = get_index()
        
        if index:
            print("✅ get_index() 成功")
            print(f"📊 索引类型: {type(index)}")
            return True
        else:
            print("❌ get_index() 返回 None")
            return False
            
    except Exception as e:
        print(f"❌ get_index() 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_creation():
    """测试工作流创建"""
    print("\n⚙️ 测试工作流创建")
    print("=" * 60)
    
    try:
        from app.workflow import create_workflow
        
        print("调用 create_workflow()...")
        workflow = create_workflow()
        
        if workflow:
            print("✅ 工作流创建成功")
            print(f"⚙️ 工作流类型: {type(workflow)}")
            return True
        else:
            print("❌ 工作流创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 工作流创建异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🔧 索引加载问题调试")
    print("=" * 80)
    
    # 逐步测试
    step_ok = test_step_by_step()
    
    if step_ok:
        print("\n" + "=" * 80)
        
        # 测试 get_index 函数
        index_ok = test_get_index_function()
        
        if index_ok:
            # 测试工作流创建
            workflow_ok = test_workflow_creation()
            
            if workflow_ok:
                print("\n🎉 所有测试通过！索引加载正常")
            else:
                print("\n❌ 工作流创建失败")
        else:
            print("\n❌ get_index 函数失败")
    else:
        print("\n❌ 基础步骤测试失败")
    
    print("\n💡 调试完成")

if __name__ == "__main__":
    main()
