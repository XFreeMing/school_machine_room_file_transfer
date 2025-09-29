#!/usr/bin/env python3
"""
跨平台构建脚本
检测操作系统并生成对应平台的可执行文件
"""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def detect_platform():
    """检测当前平台"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"


def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖包...")

    dependencies = [
        "flask>=3.1.2",
        "flask-cors>=6.0.1",
        "requests>=2.32.5",
        "pyinstaller>=6.16.0",
    ]

    for dep in dependencies:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                check=True,
                capture_output=True,
            )
            print(f"✅ 安装成功: {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 安装失败: {dep}")
            return False

    return True


def build_for_current_platform():
    """为当前平台构建"""
    current_platform = detect_platform()
    print(f"🖥️  检测到平台: {current_platform}")

    if current_platform == "windows":
        return build_windows()
    elif current_platform == "macos":
        return build_macos()
    elif current_platform == "linux":
        return build_linux()
    else:
        print(f"❌ 不支持的平台: {current_platform}")
        return False


def build_windows():
    """构建Windows版本"""
    print("🪟 构建Windows版本...")

    # 教师端
    teacher_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=教师端",
        "--add-data=data;data",
        "teacher_app.py",
    ]

    # 学生端
    student_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=学生端",
        "student_app.py",
    ]

    try:
        subprocess.run(teacher_cmd, check=True)
        print("✅ 教师端构建成功")

        subprocess.run(student_cmd, check=True)
        print("✅ 学生端构建成功")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False


def build_macos():
    """构建macOS版本"""
    print("🍎 构建macOS版本...")

    # 教师端
    teacher_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=教师端",
        "--add-data=data:data",
        "teacher_app.py",
    ]

    # 学生端
    student_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=学生端",
        "student_app.py",
    ]

    try:
        subprocess.run(teacher_cmd, check=True)
        print("✅ 教师端构建成功")

        subprocess.run(student_cmd, check=True)
        print("✅ 学生端构建成功")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False


def build_linux():
    """构建Linux版本"""
    print("🐧 构建Linux版本...")

    # 教师端
    teacher_cmd = [
        "pyinstaller",
        "--onefile",
        "--name=教师端",
        "--add-data=data:data",
        "teacher_app.py",
    ]

    # 学生端
    student_cmd = ["pyinstaller", "--onefile", "--name=学生端", "student_app.py"]

    try:
        subprocess.run(teacher_cmd, check=True)
        print("✅ 教师端构建成功")

        subprocess.run(student_cmd, check=True)
        print("✅ 学生端构建成功")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False


def create_startup_scripts():
    """创建启动脚本"""
    current_platform = detect_platform()

    if current_platform == "windows":
        # Windows批处理文件
        teacher_script = """@echo off
教师端.exe
"""
        student_script = """@echo off
学生端.exe
"""

        with open("dist/启动教师端.bat", "w", encoding="utf-8") as f:
            f.write(teacher_script)

        with open("dist/启动学生端.bat", "w", encoding="utf-8") as f:
            f.write(student_script)

    else:
        # Unix shell脚本
        teacher_script = """#!/bin/bash
./教师端
"""
        student_script = """#!/bin/bash
./学生端
"""

        with open("dist/启动教师端.sh", "w") as f:
            f.write(teacher_script)

        with open("dist/启动学生端.sh", "w") as f:
            f.write(student_script)

        # 设置执行权限
        os.chmod("dist/启动教师端.sh", 0o755)
        os.chmod("dist/启动学生端.sh", 0o755)

    print("✅ 创建启动脚本")


def main():
    """主函数"""
    print("🚀 跨平台构建脚本")
    print("=" * 50)

    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        return False

    # 创建dist目录
    Path("dist").mkdir(exist_ok=True)

    # 创建数据目录
    Path("data/teacher_files").mkdir(parents=True, exist_ok=True)
    Path("data/student_work").mkdir(parents=True, exist_ok=True)

    # 构建
    if not build_for_current_platform():
        print("❌ 构建失败")
        return False

    # 创建启动脚本
    create_startup_scripts()

    print("\n🎉 构建完成!")
    print(f"📁 输出目录: dist/")
    print(f"🖥️  目标平台: {detect_platform()}")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
