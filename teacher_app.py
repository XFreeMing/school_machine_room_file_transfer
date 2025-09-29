"""
教师端应用 - 集成文件服务器功能
既是客户端又是服务器，学生端直接连接到此
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
import socket
import json
from datetime import datetime
from pathlib import Path
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import webbrowser
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS


class FileManager:
    """文件管理类"""
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.teacher_files_dir = self.base_dir / "teacher_files"
        self.student_work_dir = self.base_dir / "student_work"
        self.metadata_file = self.base_dir / "metadata.json"
        
        # 创建必要的目录
        self.teacher_files_dir.mkdir(parents=True, exist_ok=True)
        self.student_work_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化元数据
        self.metadata = self._load_metadata()
    
    def _load_metadata(self):
        """加载文件元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {"teacher_files": {}, "student_work": {}}
    
    def _save_metadata(self):
        """保存文件元数据"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def save_teacher_file(self, file_path: str, filename: str, description: str = ""):
        """保存老师上传的文件"""
        import shutil
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        target_path = self.teacher_files_dir / unique_filename
        
        # 复制文件
        shutil.copy2(file_path, target_path)
        
        # 记录元数据
        file_id = str(len(self.metadata["teacher_files"]) + 1)
        self.metadata["teacher_files"][file_id] = {
            "original_name": filename,
            "saved_name": unique_filename,
            "description": description,
            "upload_time": datetime.now().isoformat(),
            "file_size": os.path.getsize(target_path)
        }
        
        self._save_metadata()
        
        return {
            "file_id": file_id,
            "filename": filename,
            "saved_name": unique_filename,
            "description": description,
            "upload_time": self.metadata["teacher_files"][file_id]["upload_time"],
            "file_size": self.metadata["teacher_files"][file_id]["file_size"]
        }
    
    def save_student_work(self, file_path: str, filename: str, student_name: str, description: str = ""):
        """保存学生提交的作业"""
        import shutil
        
        # 按学生姓名创建子目录
        student_dir = self.student_work_dir / student_name
        student_dir.mkdir(exist_ok=True)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        target_path = student_dir / unique_filename
        
        # 复制文件
        shutil.copy2(file_path, target_path)
        
        # 记录元数据
        work_id = str(len(self.metadata["student_work"]) + 1)
        self.metadata["student_work"][work_id] = {
            "original_name": filename,
            "saved_name": unique_filename,
            "student_name": student_name,
            "description": description,
            "upload_time": datetime.now().isoformat(),
            "file_size": os.path.getsize(target_path),
            "file_path": str(target_path.relative_to(self.base_dir))
        }
        
        self._save_metadata()
        
        return {
            "work_id": work_id,
            "filename": filename,
            "student_name": student_name,
            "description": description,
            "upload_time": self.metadata["student_work"][work_id]["upload_time"],
            "file_size": self.metadata["student_work"][work_id]["file_size"]
        }
    
    def get_teacher_files(self):
        """获取所有老师文件列表"""
        files = []
        for file_id, file_info in self.metadata["teacher_files"].items():
            files.append({
                "file_id": file_id,
                "filename": file_info["original_name"],
                "description": file_info["description"],
                "upload_time": file_info["upload_time"],
                "file_size": file_info["file_size"]
            })
        return sorted(files, key=lambda x: x["upload_time"], reverse=True)
    
    def get_student_work(self):
        """获取所有学生作业列表"""
        works = []
        for work_id, work_info in self.metadata["student_work"].items():
            works.append({
                "work_id": work_id,
                "filename": work_info["original_name"],
                "student_name": work_info["student_name"],
                "description": work_info["description"],
                "upload_time": work_info["upload_time"],
                "file_size": work_info["file_size"]
            })
        return sorted(works, key=lambda x: x["upload_time"], reverse=True)
    
    def get_teacher_file_path(self, file_id: str):
        """获取老师文件的完整路径"""
        if file_id in self.metadata["teacher_files"]:
            saved_name = self.metadata["teacher_files"][file_id]["saved_name"]
            file_path = self.teacher_files_dir / saved_name
            if file_path.exists():
                return str(file_path)
        return None
    
    def get_student_work_path(self, work_id: str):
        """获取学生作业的完整路径"""
        if work_id in self.metadata["student_work"]:
            file_path = self.base_dir / self.metadata["student_work"][work_id]["file_path"]
            if file_path.exists():
                return str(file_path)
        return None
    
    def delete_teacher_file(self, file_id: str):
        """删除老师文件"""
        if file_id in self.metadata["teacher_files"]:
            file_info = self.metadata["teacher_files"][file_id]
            file_path = self.teacher_files_dir / file_info["saved_name"]
            if file_path.exists():
                file_path.unlink()
            del self.metadata["teacher_files"][file_id]
            self._save_metadata()
            return True
        return False
    
    def delete_student_work(self, work_id: str):
        """删除学生作业"""
        if work_id in self.metadata["student_work"]:
            work_info = self.metadata["student_work"][work_id]
            file_path = self.base_dir / work_info["file_path"]
            if file_path.exists():
                file_path.unlink()
            del self.metadata["student_work"][work_id]
            self._save_metadata()
            return True
        return False


class TeacherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("教师端 - 文件传输系统")
        self.root.geometry("900x700")
        
        # 初始化文件管理器
        self.file_manager = FileManager()
        
        # 服务器相关
        self.server = None
        self.server_thread = None
        self.server_running = False
        self.server_port = 5000
        
        # 创建界面
        self.create_widgets()
        
        # 启动服务器
        self.start_server()
        
        # 加载数据
        self.refresh_data()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="教师端 - 文件传输系统", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 服务器状态区域
        server_frame = ttk.LabelFrame(main_frame, text="服务器状态", padding="10")
        server_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.server_status_var = tk.StringVar()
        self.server_status_var.set("正在启动服务器...")
        status_label = ttk.Label(server_frame, textvariable=self.server_status_var, font=("Arial", 12))
        status_label.pack(side=tk.LEFT)
        
        # 获取本机IP
        self.local_ip = self.get_local_ip()
        ip_label = ttk.Label(server_frame, text=f"学生端连接地址: http://{self.local_ip}:{self.server_port}", 
                           font=("Arial", 10), foreground="blue")
        ip_label.pack(side=tk.RIGHT)
        
        # 老师文件管理区域
        teacher_frame = ttk.LabelFrame(main_frame, text="我的文件", padding="10")
        teacher_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        teacher_frame.columnconfigure(1, weight=1)
        
        # 上传按钮
        upload_btn = ttk.Button(teacher_frame, text="上传文件", command=self.upload_file)
        upload_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 刷新按钮
        refresh_btn = ttk.Button(teacher_frame, text="刷新", command=self.refresh_teacher_files)
        refresh_btn.grid(row=0, column=1, padx=(0, 10))
        
        # 老师文件列表
        self.teacher_tree = ttk.Treeview(teacher_frame, columns=("size", "time"), show="tree headings")
        self.teacher_tree.heading("#0", text="文件名")
        self.teacher_tree.heading("size", text="大小")
        self.teacher_tree.heading("time", text="上传时间")
        self.teacher_tree.column("#0", width=300)
        self.teacher_tree.column("size", width=100)
        self.teacher_tree.column("time", width=150)
        
        # 滚动条
        teacher_scrollbar = ttk.Scrollbar(teacher_frame, orient="vertical", command=self.teacher_tree.yview)
        self.teacher_tree.configure(yscrollcommand=teacher_scrollbar.set)
        
        self.teacher_tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        teacher_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S), pady=(10, 0))
        
        # 老师文件操作按钮
        teacher_btn_frame = ttk.Frame(teacher_frame)
        teacher_btn_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        download_teacher_btn = ttk.Button(teacher_btn_frame, text="下载", command=self.download_teacher_file)
        download_teacher_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_teacher_btn = ttk.Button(teacher_btn_frame, text="删除", command=self.delete_teacher_file)
        delete_teacher_btn.pack(side=tk.LEFT)
        
        # 学生作业管理区域
        student_frame = ttk.LabelFrame(main_frame, text="学生作业", padding="10")
        student_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        student_frame.columnconfigure(1, weight=1)
        
        # 刷新学生作业按钮
        refresh_student_btn = ttk.Button(student_frame, text="刷新作业", command=self.refresh_student_work)
        refresh_student_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 学生作业列表
        self.student_tree = ttk.Treeview(student_frame, columns=("student", "size", "time"), show="tree headings")
        self.student_tree.heading("#0", text="文件名")
        self.student_tree.heading("student", text="学生姓名")
        self.student_tree.heading("size", text="大小")
        self.student_tree.heading("time", text="提交时间")
        self.student_tree.column("#0", width=250)
        self.student_tree.column("student", width=100)
        self.student_tree.column("size", width=80)
        self.student_tree.column("time", width=150)
        
        # 滚动条
        student_scrollbar = ttk.Scrollbar(student_frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=student_scrollbar.set)
        
        self.student_tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        student_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S), pady=(10, 0))
        
        # 学生作业操作按钮
        student_btn_frame = ttk.Frame(student_frame)
        student_btn_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        download_student_btn = ttk.Button(student_btn_frame, text="下载作业", command=self.download_student_work)
        download_student_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_student_btn = ttk.Button(student_btn_frame, text="删除作业", command=self.delete_student_work)
        delete_student_btn.pack(side=tk.LEFT)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def get_local_ip(self):
        """获取本机IP地址"""
        try:
            # 连接到一个远程地址来获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def start_server(self):
        """启动Flask服务器"""
        def run_server():
            app = Flask(__name__)
            CORS(app)
            
            @app.route('/api/health', methods=['GET'])
            def health_check():
                return jsonify({"status": "ok", "message": "教师端服务器运行正常"})
            
            @app.route('/api/teacher/files', methods=['GET'])
            def get_teacher_files():
                try:
                    files = self.file_manager.get_teacher_files()
                    return jsonify({"success": True, "files": files})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
            
            @app.route('/api/teacher/files', methods=['POST'])
            def upload_teacher_file():
                try:
                    if 'file' not in request.files:
                        return jsonify({"success": False, "error": "没有选择文件"}), 400
                    
                    file = request.files['file']
                    if file.filename == '':
                        return jsonify({"success": False, "error": "文件名不能为空"}), 400
                    
                    description = request.form.get('description', '')
                    
                    # 保存文件
                    result = self.file_manager.save_teacher_file(
                        file_path=file.filename,
                        filename=file.filename,
                        description=description
                    )
                    
                    # 实际保存文件
                    file_path = os.path.join(self.file_manager.teacher_files_dir, result['saved_name'])
                    file.save(file_path)
                    
                    return jsonify({"success": True, "file": result})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
            
            @app.route('/api/teacher/files/<file_id>', methods=['GET'])
            def download_teacher_file(file_id):
                try:
                    file_path = self.file_manager.get_teacher_file_path(file_id)
                    if not file_path:
                        return jsonify({"success": False, "error": "文件不存在"}), 404
                    
                    return send_file(file_path, as_attachment=True)
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
            
            @app.route('/api/student/work', methods=['GET'])
            def get_student_work():
                try:
                    works = self.file_manager.get_student_work()
                    return jsonify({"success": True, "works": works})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
            
            @app.route('/api/student/work', methods=['POST'])
            def upload_student_work():
                try:
                    if 'file' not in request.files:
                        return jsonify({"success": False, "error": "没有选择文件"}), 400
                    
                    file = request.files['file']
                    if file.filename == '':
                        return jsonify({"success": False, "error": "文件名不能为空"}), 400
                    
                    student_name = request.form.get('student_name', '')
                    if not student_name:
                        return jsonify({"success": False, "error": "学生姓名不能为空"}), 400
                    
                    description = request.form.get('description', '')
                    
                    # 保存文件
                    result = self.file_manager.save_student_work(
                        file_path=file.filename,
                        filename=file.filename,
                        student_name=student_name,
                        description=description
                    )
                    
                    # 实际保存文件
                    student_dir = self.file_manager.student_work_dir / student_name
                    student_dir.mkdir(exist_ok=True)
                    file_path = os.path.join(student_dir, result['saved_name'])
                    file.save(file_path)
                    
                    return jsonify({"success": True, "work": result})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
            
            @app.route('/api/student/work/<work_id>', methods=['GET'])
            def download_student_work(work_id):
                try:
                    file_path = self.file_manager.get_student_work_path(work_id)
                    if not file_path:
                        return jsonify({"success": False, "error": "文件不存在"}), 404
                    
                    return send_file(file_path, as_attachment=True)
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
            
            try:
                self.server_running = True
                self.server_status_var.set(f"服务器运行中 - http://{self.local_ip}:{self.server_port}")
                app.run(host='0.0.0.0', port=self.server_port, debug=False, use_reloader=False)
            except Exception as e:
                self.server_running = False
                self.server_status_var.set(f"服务器启动失败: {str(e)}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
    
    def refresh_data(self):
        """刷新所有数据"""
        self.refresh_teacher_files()
        self.refresh_student_work()
    
    def refresh_teacher_files(self):
        """刷新老师文件列表"""
        files = self.file_manager.get_teacher_files()
        
        # 清空现有项目
        for item in self.teacher_tree.get_children():
            self.teacher_tree.delete(item)
        
        # 添加文件到列表
        for file_info in files:
            file_size = self.format_file_size(file_info.get('file_size', 0))
            upload_time = file_info.get('upload_time', '')[:19].replace('T', ' ')
            
            self.teacher_tree.insert("", "end", 
                text=file_info.get('filename', ''),
                values=(file_size, upload_time),
                tags=(file_info.get('file_id', ''),))
    
    def refresh_student_work(self):
        """刷新学生作业列表"""
        works = self.file_manager.get_student_work()
        
        # 清空现有项目
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # 添加作业到列表
        for work_info in works:
            file_size = self.format_file_size(work_info.get('file_size', 0))
            upload_time = work_info.get('upload_time', '')[:19].replace('T', ' ')
            
            self.student_tree.insert("", "end",
                text=work_info.get('filename', ''),
                values=(work_info.get('student_name', ''), file_size, upload_time),
                tags=(work_info.get('work_id', ''),))
    
    def upload_file(self):
        """上传文件"""
        file_path = filedialog.askopenfilename(
            title="选择要上传的文件",
            filetypes=[("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        # 获取文件描述
        description = tk.simpledialog.askstring("文件描述", "请输入文件描述（可选）:")
        if description is None:
            return
        
        def upload():
            self.status_var.set("正在上传文件...")
            try:
                result = self.file_manager.save_teacher_file(file_path, os.path.basename(file_path), description or "")
                messagebox.showinfo("成功", "文件上传成功！")
                self.refresh_teacher_files()
            except Exception as e:
                messagebox.showerror("错误", f"上传失败：{str(e)}")
            
            self.status_var.set("就绪")
        
        threading.Thread(target=upload, daemon=True).start()
    
    def download_teacher_file(self):
        """下载老师文件"""
        selection = self.teacher_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要下载的文件")
            return
        
        item = self.teacher_tree.item(selection[0])
        file_id = item['tags'][0] if item['tags'] else None
        filename = item['text']
        
        if not file_id:
            messagebox.showerror("错误", "无法获取文件ID")
            return
        
        # 选择保存位置
        save_path = filedialog.asksaveasfilename(
            title="选择保存位置",
            initialvalue=filename,
            filetypes=[("所有文件", "*.*")]
        )
        
        if not save_path:
            return
        
        def download():
            self.status_var.set("正在下载文件...")
            try:
                file_path = self.file_manager.get_teacher_file_path(file_id)
                if file_path:
                    import shutil
                    shutil.copy2(file_path, save_path)
                    messagebox.showinfo("成功", "文件下载成功！")
                else:
                    messagebox.showerror("错误", "文件不存在")
            except Exception as e:
                messagebox.showerror("错误", f"下载失败：{str(e)}")
            
            self.status_var.set("就绪")
        
        threading.Thread(target=download, daemon=True).start()
    
    def delete_teacher_file(self):
        """删除老师文件"""
        selection = self.teacher_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的文件")
            return
        
        item = self.teacher_tree.item(selection[0])
        filename = item['text']
        file_id = item['tags'][0] if item['tags'] else None
        
        if not file_id:
            messagebox.showerror("错误", "无法获取文件ID")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除文件 '{filename}' 吗？"):
            try:
                success = self.file_manager.delete_teacher_file(file_id)
                if success:
                    messagebox.showinfo("成功", "文件删除成功！")
                    self.refresh_teacher_files()
                else:
                    messagebox.showerror("错误", "删除失败")
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")
    
    def download_student_work(self):
        """下载学生作业"""
        selection = self.student_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要下载的作业")
            return
        
        item = self.student_tree.item(selection[0])
        work_id = item['tags'][0] if item['tags'] else None
        filename = item['text']
        student_name = item['values'][0]
        
        if not work_id:
            messagebox.showerror("错误", "无法获取作业ID")
            return
        
        # 选择保存位置
        save_path = filedialog.asksaveasfilename(
            title="选择保存位置",
            initialvalue=f"{student_name}_{filename}",
            filetypes=[("所有文件", "*.*")]
        )
        
        if not save_path:
            return
        
        def download():
            self.status_var.set("正在下载作业...")
            try:
                file_path = self.file_manager.get_student_work_path(work_id)
                if file_path:
                    import shutil
                    shutil.copy2(file_path, save_path)
                    messagebox.showinfo("成功", "作业下载成功！")
                else:
                    messagebox.showerror("错误", "作业不存在")
            except Exception as e:
                messagebox.showerror("错误", f"下载失败：{str(e)}")
            
            self.status_var.set("就绪")
        
        threading.Thread(target=download, daemon=True).start()
    
    def delete_student_work(self):
        """删除学生作业"""
        selection = self.student_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的作业")
            return
        
        item = self.student_tree.item(selection[0])
        filename = item['text']
        student_name = item['values'][0]
        work_id = item['tags'][0] if item['tags'] else None
        
        if not work_id:
            messagebox.showerror("错误", "无法获取作业ID")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除 {student_name} 的作业 '{filename}' 吗？"):
            try:
                success = self.file_manager.delete_student_work(work_id)
                if success:
                    messagebox.showinfo("成功", "作业删除成功！")
                    self.refresh_student_work()
                else:
                    messagebox.showerror("错误", "删除失败")
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")
    
    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def run(self):
        """运行应用"""
        self.root.mainloop()


if __name__ == "__main__":
    import tkinter.simpledialog
    app = TeacherApp()
    app.run()
