#!/usr/bin/env python3
"""
构建脚本 - 用于打包教师端和学生端为exe文件
"""
# 移除未使用的 os 导入
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """运行命令并显示进度"""
    print(f"\n{'='*50}")
    print(f"正在{description}...")
    print(f"命令: {cmd}")
    print("=" * 50)

    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print("✅ 成功!")
        if result.stdout:
            print("输出:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {e}")
        if e.stdout:
            print("输出:", e.stdout)
        if e.stderr:
            print("错误:", e.stderr)
        return False


def main():
    """主构建流程"""
    print("🚀 开始构建学校机房文件传输系统...")
    print("📋 新架构：教师端集成服务器，学生端自动连接")

    # 检查uv是否安装
    if not shutil.which("uv"):
        print("❌ 错误: 未找到uv，请先安装uv")
        print("安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

    # 安装依赖
    if not run_command("uv sync", "安装依赖"):
        return False

    # 创建dist目录
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)

    # 先创建数据目录（PyInstaller 在 teacher spec 中需要预先存在的 data 目录）
    data_dirs = ["data", "data/teacher_files", "data/student_work"]
    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ 预创建数据目录供打包使用")

    # 构建教师端
    print("\n👨‍🏫 构建教师端...")
    if not run_command("uv run pyinstaller build_teacher.spec", "打包教师端"):
        return False

    # 构建学生端
    print("\n👨‍🎓 构建学生端...")
    if not run_command("uv run pyinstaller build_student.spec", "打包学生端"):
        return False

    # 复制exe文件到dist目录
    print("\n📦 整理输出文件...")

    # 检查生成的文件（macOS上可能没有.exe扩展名）
    teacher_exe = (
        "dist/教师端.exe" if Path("dist/教师端.exe").exists() else "dist/教师端"
    )
    student_exe = (
        "dist/学生端.exe" if Path("dist/学生端.exe").exists() else "dist/学生端"
    )

    exe_files = [
        (teacher_exe, "dist/教师端.exe"),
        (student_exe, "dist/学生端.exe"),
    ]

    for src, dst in exe_files:
        if Path(src).exists():
            if src != dst:  # 避免复制到同一个文件
                shutil.copy2(src, dst)
                print(f"✅ 复制 {src} -> {dst}")
            else:
                print(f"✅ 文件已存在 {src}")
        else:
            print(f"⚠️  未找到 {src}")

    # 创建启动脚本
    create_startup_scripts()

    print("\n🎉 构建完成!")
    print("\n📁 输出目录: dist/")
    print("📋 包含文件:")
    print("  - 教师端.exe (集成服务器功能)")
    print("  - 学生端.exe (自动连接教师端)")
    print("  - 启动教师端.bat (Windows启动脚本)")
    print("  - 启动学生端.bat (Windows启动脚本)")
    print("\n🚀 使用方法:")
    print("  1. 在教师电脑运行'教师端.exe'")
    print("  2. 在学生电脑运行'学生端.exe'")
    print("  3. 学生端会自动发现并连接教师端")

    return True


def create_startup_scripts():
    """创建启动脚本"""

    # 教师端启动脚本
    teacher_script = """@echo off
echo Starting Teacher Client...
echo Teacher client includes file server functionality
echo Student clients will automatically connect to this machine
echo.
教师端.exe
pause
"""

    with open("dist/启动教师端.bat", "w", encoding="utf-8") as f:
        f.write(teacher_script)

    # 学生端启动脚本
    student_script = """@echo off
echo Starting Student Client...
echo Automatically searching for teacher client...
echo Please ensure teacher client is running
echo.
学生端.exe
pause
"""

    with open("dist/启动学生端.bat", "w", encoding="utf-8") as f:
        f.write(student_script)

    print("✅ 创建启动脚本")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
