# Windows 构建指南

## 问题说明

在 macOS 上构建的 exe 文件实际上是 Mach-O 格式，无法在 Windows 上运行。需要在 Windows 机器上重新构建。

## Windows 构建步骤

### 1. 环境准备

- Windows 10/11
- Python 3.13
- 网络连接

### 2. 安装 Python

```cmd
# 下载并安装Python 3.13
# 从 https://www.python.org/downloads/ 下载
# 安装时勾选 "Add Python to PATH"
```

### 3. 安装依赖

```cmd
pip install flask flask-cors requests pyinstaller
```

### 4. 构建程序

```cmd
# 将整个项目文件夹复制到Windows机器
# 在项目目录运行：
python build.py
```

### 5. 验证构建

构建完成后，dist 目录应该包含：

- 教师端.exe (Windows PE 格式)
- 学生端.exe (Windows PE 格式)
- 启动教师端.bat
- 启动学生端.bat

## 故障排除

### 如果 pip 安装失败

```cmd
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple flask flask-cors requests pyinstaller
```

### 如果 PyInstaller 构建失败

```cmd
# 检查Python版本
python --version

# 重新安装PyInstaller
pip uninstall pyinstaller
pip install pyinstaller
```

### 如果 exe 文件仍然无法运行

1. 检查 Windows Defender 是否阻止了文件
2. 右键 exe 文件，选择"以管理员身份运行"
3. 检查是否缺少 Visual C++ Redistributable
