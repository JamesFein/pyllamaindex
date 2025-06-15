#!/usr/bin/env python3
"""
测试流式API
"""
import requests
import json
import time
from urllib.parse import urlencode

def test_streaming_api():
    """测试流式聊天API"""
    base_url = "http://localhost:8000"
    
    # 准备请求数据
    chat_data = {
        "id": f"test_stream_{int(time.time())}",
        "messages": [
            {
                "role": "user",
                "content": "电子发票重复报销如何防范？"
            }
        ],
        "data": {}
    }
    
    # 构建URL
    params = {"data": json.dumps(chat_data)}
    url = f"{base_url}/api/chat/stream?{urlencode(params)}"
    
    print(f"测试流式API: {url}")
    print("=" * 50)
    
    try:
        # 发送GET请求到流式端点
        response = requests.get(url, stream=True, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print("=" * 50)
        
        if response.status_code == 200:
            print("开始接收流式数据:")
            print("-" * 30)
            
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(f"收到数据: {line}")
                    
                    # 解析SSE数据
                    if line.startswith("data: "):
                        data_content = line[6:]  # 移除 "data: " 前缀
                        try:
                            data = json.loads(data_content)
                            print(f"解析后数据: {data}")
                        except json.JSONDecodeError:
                            print(f"无法解析JSON: {data_content}")
                    elif line.startswith("event: "):
                        event_type = line[7:]  # 移除 "event: " 前缀
                        print(f"事件类型: {event_type}")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

def test_regular_api():
    """测试普通聊天API作为对比"""
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
        print("响应内容:")
        print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    print("开始测试...")
    print("\n1. 测试普通API:")
    test_regular_api()
    
    print("\n\n2. 测试流式API:")
    test_streaming_api()
