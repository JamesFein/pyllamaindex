#!/usr/bin/env python3
"""
测试LlamaIndex服务器API的脚本
"""

import requests
import json
import time

def test_chat_api():
    """测试chat API并检查响应格式"""
    url = "http://localhost:8000/api/chat"

    payload = {
        "id": "test-123",
        "messages": [
            {
                "role": "user",
                "content": "发票丢失了怎么办？"
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("发送请求到:", url)
    print("请求数据:", json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n流式响应内容:")
            content = ""
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    print(f"收到块: {repr(chunk)}")
                    content += chunk
            
            print(f"\n完整响应内容:\n{content}")
            
            # 尝试解析是否包含sources注解
            if "sources" in content.lower():
                print("\n✅ 响应中包含sources相关内容")
            else:
                print("\n❌ 响应中未找到sources相关内容")
                
            if "[citation:" in content:
                print("✅ 响应中包含citation标记")
            else:
                print("❌ 响应中未找到citation标记")
                
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求出错: {e}")

def test_health_api():
    """测试健康检查API"""
    url = "http://localhost:8000/api/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"健康检查状态码: {response.status_code}")
        print(f"健康检查响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

if __name__ == "__main__":
    print("=== LlamaIndex服务器API测试 ===\n")
    
    # 先测试健康检查
    if test_health_api():
        print("\n✅ 服务器运行正常，开始测试chat API\n")
        test_chat_api()
    else:
        print("\n❌ 服务器未运行或健康检查失败")
