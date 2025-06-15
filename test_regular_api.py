#!/usr/bin/env python3
"""
测试普通API的响应格式
"""
import requests
import json
import time

def test_regular_api():
    """测试普通聊天API"""
    url = "http://localhost:8000/api/chat"
    
    payload = {
        "id": f"test_regular_{int(time.time())}",
        "messages": [
            {
                "role": "user",
                "content": "电子发票重复报销如何防范？"
            }
        ],
        "data": {}
    }
    
    print(f"测试普通API: {url}")
    print("=" * 50)
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print("完整响应内容:")
        print(response.text)
        print("=" * 50)
        
        # 检查是否包含引用数据
        if "CITATION_DATA:" in response.text:
            print("✅ 发现引用数据!")
        else:
            print("❌ 未发现引用数据")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_regular_api()
