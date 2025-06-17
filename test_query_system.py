#!/usr/bin/env python3
"""
测试查询系统是否正常工作
"""
import os
from dotenv import load_dotenv

def test_query_engine():
    """测试查询引擎"""
    print("🔍 测试查询引擎")
    print("=" * 60)
    
    try:
        # 加载环境变量
        load_dotenv()
        
        # 初始化设置
        from app.settings import init_settings
        init_settings()
        
        # 加载存储上下文
        from app.storage_config import load_storage_context
        from app.index import STORAGE_DIR
        
        storage_context = load_storage_context(STORAGE_DIR)
        if not storage_context:
            print("❌ 无法加载存储上下文")
            return False
        
        print("✅ 存储上下文加载成功")
        
        # 创建查询引擎
        from llama_index.core.indices import VectorStoreIndex
        
        index = VectorStoreIndex.from_vector_store(
            storage_context.vector_store,
            storage_context=storage_context
        )
        
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )
        
        print("✅ 查询引擎创建成功")
        
        # 测试查询
        test_queries = [
            "AI智能助手有什么功能？",
            "产品信息",
            "测试文档内容"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 测试查询 {i}: {query}")
            try:
                response = query_engine.query(query)
                print(f"✅ 查询成功")
                print(f"📄 响应长度: {len(str(response))} 字符")
                print(f"📄 响应预览: {str(response)[:100]}...")
                
                # 检查源节点
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    print(f"📚 找到 {len(response.source_nodes)} 个相关文档块")
                    for j, node in enumerate(response.source_nodes):
                        file_name = node.metadata.get('file_name', 'Unknown')
                        chunk_index = node.metadata.get('chunk_index', 'Unknown')
                        score = getattr(node, 'score', 'Unknown')
                        print(f"  块 {j+1}: {file_name} chunk_{chunk_index} (相似度: {score})")
                else:
                    print("⚠️  没有找到源节点")
                    
            except Exception as e:
                print(f"❌ 查询失败: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_api_endpoint():
    """测试 API 端点"""
    print("\n🌐 测试 API 端点")
    print("=" * 60)
    
    try:
        import requests
        import json
        
        # 测试查询 API
        url = "http://localhost:8000/api/chat"
        payload = {
            "id": "test-session",
            "messages": [
                {
                    "role": "user", 
                    "content": "AI智能助手有什么功能？"
                }
            ]
        }
        
        print("📡 发送 API 请求...")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("✅ API 请求成功")
            
            # 尝试解析响应
            try:
                data = response.json()
                print(f"📄 响应数据类型: {type(data)}")
                if isinstance(data, dict):
                    print(f"📄 响应字段: {list(data.keys())}")
                print(f"📄 响应长度: {len(str(data))} 字符")
            except:
                print(f"📄 响应内容: {response.text[:200]}...")
                
        else:
            print(f"❌ API 请求失败: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器 (请确保服务器正在运行)")
        return False
    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 查询系统完整性测试")
    print("=" * 80)
    
    # 测试查询引擎
    engine_ok = test_query_engine()
    
    # 测试 API 端点
    api_ok = test_api_endpoint()
    
    print("\n📊 测试结果总结")
    print("=" * 60)
    print(f"查询引擎: {'✅ 正常' if engine_ok else '❌ 异常'}")
    print(f"API 端点: {'✅ 正常' if api_ok else '❌ 异常'}")
    
    if engine_ok and api_ok:
        print("\n🎉 系统运行正常！")
        print("💡 建议:")
        print("  1. 通过前端界面测试用户交互")
        print("  2. 测试文档上传和删除功能")
        print("  3. 验证引用显示是否正确")
    else:
        print("\n⚠️  系统存在问题，需要进一步调试")

if __name__ == "__main__":
    main()
