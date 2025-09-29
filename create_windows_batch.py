#!/usr/bin/env python3
"""
创建Windows兼容的批处理文件
"""
import os


def create_windows_batch_files():
    """创建Windows兼容的批处理文件"""

    # 教师端批处理文件
    teacher_bat = """@echo off
chcp 65001 >nul
echo Starting Teacher Client...
echo Teacher client includes file server functionality
echo Student clients will automatically connect to this machine
echo.
教师端.exe
pause
"""

    # 学生端批处理文件
    student_bat = """@echo off
chcp 65001 >nul
echo Starting Student Client...
echo Automatically searching for teacher client...
echo Please ensure teacher client is running
echo.
学生端.exe
pause
"""

    # 写入文件，使用UTF-8编码
    with open("dist/启动教师端.bat", "w", encoding="utf-8") as f:
        f.write(teacher_bat)

    with open("dist/启动学生端.bat", "w", encoding="utf-8") as f:
        f.write(student_bat)

    print("✅ 创建Windows兼容的批处理文件")


if __name__ == "__main__":
    create_windows_batch_files()
