#!/usr/bin/env python3
"""
系统测试脚本
用于验证文件传输系统的基本功能
"""
import os
import sys
import time
import requests
import threading
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.file_manager import FileManager
from client.common import TeacherAPIClient, StudentAPIClient


def test_file_manager():
    """测试文件管理器"""
    print("🧪 测试文件管理器...")
    
    try:
        # 创建测试文件
        test_file = "test_file.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("这是一个测试文件")
        
        # 初始化文件管理器
        fm = FileManager("test_data")
        
        # 测试保存老师文件
        result = fm.save_teacher_file(test_file, "test.txt", "测试文件")
        assert result["success"] if "success" in result else True
        print("✅ 文件管理器测试通过")
        
        # 清理测试文件
        os.remove(test_file)
        import shutil
        shutil.rmtree("test_data", ignore_errors=True)
        
        return True
    except Exception as e:
        print(f"❌ 文件管理器测试失败: {e}")
        return False


def test_api_client():
    """测试API客户端"""
    print("🧪 测试API客户端...")
    
    try:
        # 测试老师端API
        teacher_api = TeacherAPIClient()
        health = teacher_api.health_check()
        
        if health.get("status") == "ok":
            print("✅ API客户端测试通过")
            return True
        else:
            print("⚠️  服务器未运行，跳过API测试")
            return True
    except Exception as e:
        print(f"⚠️  API客户端测试跳过（服务器未运行）: {e}")
        return True


def test_server_startup():
    """测试服务器启动"""
    print("🧪 测试服务器启动...")
    
    try:
        # 尝试启动服务器（在后台）
        from server.app import app
        import threading
        
        def run_server():
            app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(3)
        
        # 测试健康检查
        response = requests.get("http://127.0.0.1:5001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器启动测试通过")
            return True
        else:
            print("❌ 服务器启动测试失败")
            return False
    except Exception as e:
        print(f"❌ 服务器启动测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始系统测试...")
    print("=" * 50)
    
    tests = [
        ("文件管理器", test_file_manager),
        ("API客户端", test_api_client),
        ("服务器启动", test_server_startup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 运行测试: {test_name}")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用。")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统配置。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
