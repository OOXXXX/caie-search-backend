#!/usr/bin/env python3
"""
API功能测试脚本
用于验证CAIE搜题系统的各项功能
"""

import requests
import time
import json
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🏥 测试健康检查...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过")
            print(f"   - Elasticsearch: {'✅' if data['status']['elasticsearch'] else '❌'}")
            print(f"   - Redis: {'✅' if data['status']['redis'] else '❌'}")
            print(f"   - OCR: {'✅' if data['status']['ocr'] else '❌'}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_text_search():
    """测试文本搜索"""
    print("\n🔍 测试文本搜索...")
    
    test_queries = [
        "differentiate",
        "integrate", 
        "solve equation",
        "graph",
        "matrix"
    ]
    
    for query in test_queries:
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE}/search/text",
                json={"query": query, "limit": 3}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ 搜索 '{query}': {len(results)} 结果, {end_time-start_time:.2f}秒")
                
                if results:
                    # 显示第一个结果
                    first_result = results[0]
                    print(f"   📝 {first_result['title']}")
                    print(f"   📅 {first_result['year']} {first_result['season']}")
                    print(f"   🎯 置信度: {first_result['confidence']:.2f}")
            else:
                print(f"❌ 搜索 '{query}' 失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 搜索 '{query}' 异常: {e}")

def test_create_index():
    """测试创建索引"""
    print("\n🔨 测试创建搜索索引...")
    try:
        response = requests.post(f"{API_BASE}/admin/index")
        if response.status_code == 200:
            print("✅ 索引创建任务已启动")
            print("⏳ 请等待几分钟让索引构建完成...")
        else:
            print(f"❌ 创建索引失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 创建索引异常: {e}")

def test_stats():
    """测试统计信息"""
    print("\n📊 测试系统统计...")
    try:
        response = requests.get(f"{API_BASE}/admin/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 统计信息:")
            print(f"   📄 文档数量: {stats['total_documents']}")
            print(f"   💾 索引大小: {stats['index_size']}")
        else:
            print(f"❌ 获取统计失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取统计异常: {e}")

def test_api_docs():
    """测试API文档"""
    print("\n📖 测试API文档...")
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            print("✅ API文档可访问")
            print(f"   🌐 地址: {API_BASE}/docs")
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档异常: {e}")

def performance_test():
    """性能测试"""
    print("\n⚡ 性能测试...")
    
    queries = ["differentiate function", "solve equation", "integrate"]
    total_time = 0
    
    for query in queries:
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE}/search/text",
                json={"query": query, "limit": 10}
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ '{query}': {response_time:.2f}秒, {len(results)} 结果")
            else:
                print(f"❌ '{query}': 请求失败")
                
        except Exception as e:
            print(f"❌ '{query}': {e}")
    
    avg_time = total_time / len(queries)
    print(f"📈 平均响应时间: {avg_time:.2f}秒")
    
    if avg_time < 2.0:
        print("🎉 性能测试通过! (< 2秒)")
    else:
        print("⚠️  响应时间较慢，建议优化")

def main():
    """主测试函数"""
    print("🚀 CAIE搜题系统API测试")
    print("=" * 50)
    
    # 1. 健康检查
    if not test_health():
        print("\n❌ 系统未正常启动，请检查:")
        print("   1. Docker容器是否运行: docker-compose ps")
        print("   2. API服务器是否启动: python main.py")
        return
    
    # 2. API文档测试
    test_api_docs()
    
    # 3. 创建索引（如果需要）
    test_create_index()
    
    # 等待一段时间让索引构建
    print("\n⏳ 等待索引构建（10秒）...")
    time.sleep(10)
    
    # 4. 统计信息
    test_stats()
    
    # 5. 文本搜索测试
    test_text_search()
    
    # 6. 性能测试
    performance_test()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成!")
    print("\n📱 下一步:")
    print("   1. 如果所有测试通过，可以开始集成到iOS App")
    print("   2. 如果有问题，查看控制台日志排查")
    print("   3. 访问 http://localhost:8000/docs 查看完整API文档")

if __name__ == "__main__":
    main()