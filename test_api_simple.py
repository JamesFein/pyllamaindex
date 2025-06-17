#!/usr/bin/env python3
"""
简单的 API 测试
"""
import requests
import json

def test_health():
    """测试健康检查"""
    try:
        response = requests.get('http://localhost:8000/api/health', timeout=5)
        print(f"健康检查: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_chat():
    """测试聊天 API"""
    url = 'http://localhost:8000/api/chat'
    payload = {
        "id": "test-session",
        "messages": [
            {
                "role": "user",
                "content": "AI智能助手有什么功能？"
            }
        ]
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        print("发送聊天请求...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 聊天 API 成功")
            print(f"响应长度: {len(response.text)} 字符")
            print(f"响应内容: {response.text[:500]}...")
            return True
        else:
            print("❌ 聊天 API 失败")
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"聊天 API 异常: {e}")
        return False

def main():
    print("🧪 简单 API 测试")
    print("=" * 50)
    
    # 测试健康检查
    if test_health():
        print("\n✅ 健康检查通过，测试聊天 API...")
        test_chat()
    else:
        print("\n❌ 健康检查失败，服务器可能未运行")

if __name__ == "__main__":
    main()
