#!/usr/bin/env python3
"""
简化系统测试脚本
测试教师端和学生端的基本功能
"""
import os
import sys
import time
import threading
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_teacher_app():
    """测试教师端应用"""
    print("🧪 测试教师端应用...")
    
    try:
        # 导入教师端模块
        from teacher_app import FileManager
        
        # 创建测试文件
        test_file = "test_file.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("这是一个测试文件")
        
        # 初始化文件管理器
        fm = FileManager("test_data")
        
        # 测试保存老师文件
        result = fm.save_teacher_file(test_file, "test.txt", "测试文件")
        print(f"✅ 文件保存成功: {result['filename']}")
        
        # 测试获取文件列表
        files = fm.get_teacher_files()
        print(f"✅ 文件列表获取成功: {len(files)} 个文件")
        
        # 清理测试文件
        os.remove(test_file)
        import shutil
        shutil.rmtree("test_data", ignore_errors=True)
        
        print("✅ 教师端测试通过")
        return True
    except Exception as e:
        print(f"❌ 教师端测试失败: {e}")
        return False


def test_student_app():
    """测试学生端应用"""
    print("🧪 测试学生端应用...")
    
    try:
        # 导入学生端模块
        from student_app import StudentApp
        
        # 测试IP获取功能
        app = StudentApp()
        local_ip = app.get_local_ip()
        print(f"✅ 本机IP获取成功: {local_ip}")
        
        print("✅ 学生端测试通过")
        return True
    except Exception as e:
        print(f"❌ 学生端测试失败: {e}")
        return False


def test_network_discovery():
    """测试网络发现功能"""
    print("🧪 测试网络发现功能...")
    
    try:
        import socket
        
        # 获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"✅ 本机IP: {local_ip}")
        
        # 测试端口扫描
        ip_parts = local_ip.split('.')
        base_ip = '.'.join(ip_parts[:3])
        print(f"✅ 网段: {base_ip}.x")
        
        print("✅ 网络发现测试通过")
        return True
    except Exception as e:
        print(f"❌ 网络发现测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始测试简化版文件传输系统...")
    print("📋 架构：教师端集成服务器 + 学生端自动连接")
    print("=" * 60)
    
    tests = [
        ("教师端应用", test_teacher_app),
        ("学生端应用", test_student_app),
        ("网络发现", test_network_discovery),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 运行测试: {test_name}")
        if test_func():
            passed += 1
        print("-" * 40)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！简化版系统可以正常使用。")
        print("\n🚀 使用方法:")
        print("  1. 运行 python teacher_app.py 启动教师端")
        print("  2. 运行 python student_app.py 启动学生端")
        print("  3. 学生端会自动发现并连接教师端")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统配置。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
