#!/usr/bin/env python3
"""
测试文件上传API的脚本
"""
import requests
import os

def test_upload():
    # 测试文件路径
    file_path = "test_upload.txt"
    
    if not os.path.exists(file_path):
        print(f"测试文件 {file_path} 不存在")
        return
    
    # API端点
    url = "http://127.0.0.1:8000/api/documents/upload"
    
    # 准备文件
    with open(file_path, 'rb') as f:
        files = {'files': (os.path.basename(file_path), f, 'text/plain')}
        
        print(f"正在上传文件: {file_path}")
        print(f"文件名: {os.path.basename(file_path)}")
        
        try:
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 上传成功!")
                print(f"响应: {result}")
                
                # 检查结果
                if 'results' in result:
                    for r in result['results']:
                        print(f"文件: {r.get('filename')}")
                        print(f"状态: {r.get('status')}")
                        print(f"消息: {r.get('message')}")
                        if 'file_id' in r:
                            print(f"文件ID: {r.get('file_id')}")
            else:
                print(f"❌ 上传失败: {response.status_code}")
                print(f"错误: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def check_documents():
    """检查当前文档列表"""
    url = "http://127.0.0.1:8000/api/documents"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print("\n📋 当前文档列表:")
            if 'documents' in result:
                for doc in result['documents']:
                    print(f"- {doc.get('name')} (ID: {doc.get('id')})")
            else:
                print("无文档")
        else:
            print(f"❌ 获取文档列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("=== 文件上传测试 ===")
    
    # 先检查当前文档
    check_documents()
    
    # 执行上传测试
    test_upload()
    
    # 再次检查文档列表
    print("\n=== 上传后的文档列表 ===")
    check_documents()
