"""
学生端应用 - 手动输入教师端地址连接
"""

import os
import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

import requests


class StudentApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("学生端 - 文件传输系统")
        self.root.geometry("700x500")

        # 学生姓名
        self.student_name = ""

        # 教师端连接信息（改为手动输入）
        self.teacher_ip = None
        self.teacher_port = 5000
        self.base_url = None

        # 创建界面
        self.create_widgets()

        # 获取学生姓名
        self.get_student_name()

    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # 标题
        title_label = ttk.Label(
            main_frame, text="学生端 - 文件传输系统", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 学生信息区域
        info_frame = ttk.LabelFrame(main_frame, text="学生信息", padding="10")
        info_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        self.student_name_label = ttk.Label(
            info_frame, text="学生姓名：未设置", font=("Arial", 12)
        )
        self.student_name_label.pack(side=tk.LEFT)

        change_name_btn = ttk.Button(
            info_frame, text="修改姓名", command=self.change_student_name
        )
        change_name_btn.pack(side=tk.RIGHT)

        # 连接状态区域（改造：加入IP/端口输入与连接按钮）
        connection_frame = ttk.LabelFrame(main_frame, text="连接教师端", padding="10")
        connection_frame.grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        ttk.Label(connection_frame, text="教师端IP：").grid(
            row=0, column=0, sticky=tk.W
        )
        self.ip_var = tk.StringVar()
        self.ip_var.set("")
        ip_entry = ttk.Entry(connection_frame, textvariable=self.ip_var, width=18)
        ip_entry.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)

        ttk.Label(connection_frame, text="端口：").grid(row=0, column=2, sticky=tk.W)
        self.port_var = tk.StringVar(value=str(self.teacher_port))
        port_entry = ttk.Entry(connection_frame, textvariable=self.port_var, width=6)
        port_entry.grid(row=0, column=3, padx=(0, 10), sticky=tk.W)

        connect_btn = ttk.Button(
            connection_frame, text="连接", command=self.connect_teacher
        )
        connect_btn.grid(row=0, column=4, padx=(0, 10))

        refresh_files_btn = ttk.Button(
            connection_frame, text="刷新文件", command=self.refresh_teacher_files
        )
        refresh_files_btn.grid(row=0, column=5)

        self.connection_status_var = tk.StringVar(value="未连接")
        status_label = ttk.Label(
            connection_frame,
            textvariable=self.connection_status_var,
            font=("Arial", 11),
        )
        status_label.grid(row=1, column=0, columnspan=6, sticky=tk.W, pady=(8, 0))

        # 老师文件区域
        teacher_frame = ttk.LabelFrame(main_frame, text="老师文件", padding="10")
        teacher_frame.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        teacher_frame.columnconfigure(1, weight=1)

        # 刷新按钮
        refresh_btn = ttk.Button(
            teacher_frame, text="刷新文件", command=self.refresh_teacher_files
        )
        refresh_btn.grid(row=0, column=0, padx=(0, 10))

        # 老师文件列表
        self.teacher_tree = ttk.Treeview(
            teacher_frame, columns=("size", "time"), show="tree headings"
        )
        self.teacher_tree.heading("#0", text="文件名")
        self.teacher_tree.heading("size", text="大小")
        self.teacher_tree.heading("time", text="上传时间")
        self.teacher_tree.column("#0", width=300)
        self.teacher_tree.column("size", width=100)
        self.teacher_tree.column("time", width=150)

        # 滚动条
        teacher_scrollbar = ttk.Scrollbar(
            teacher_frame, orient="vertical", command=self.teacher_tree.yview
        )
        self.teacher_tree.configure(yscrollcommand=teacher_scrollbar.set)

        self.teacher_tree.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0)
        )
        teacher_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S), pady=(10, 0))

        # 下载按钮
        download_btn = ttk.Button(
            teacher_frame, text="下载文件", command=self.download_file
        )
        download_btn.grid(row=2, column=0, pady=(10, 0))

        # 作业上传区域
        work_frame = ttk.LabelFrame(main_frame, text="作业上传", padding="10")
        work_frame.grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        work_frame.columnconfigure(1, weight=1)

        # 选择文件按钮
        select_file_btn = ttk.Button(
            work_frame, text="选择作业文件", command=self.select_work_file
        )
        select_file_btn.grid(row=0, column=0, padx=(0, 10))

        # 文件路径显示
        self.file_path_var = tk.StringVar()
        self.file_path_var.set("未选择文件")
        file_path_label = ttk.Label(
            work_frame, textvariable=self.file_path_var, foreground="gray"
        )
        file_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # 上传按钮
        upload_btn = ttk.Button(work_frame, text="上传作业", command=self.upload_work)
        upload_btn.grid(row=0, column=2)

        # 作业描述
        ttk.Label(work_frame, text="作业描述：").grid(
            row=1, column=0, sticky=tk.W, pady=(10, 0)
        )
        self.description_var = tk.StringVar()
        description_entry = ttk.Entry(work_frame, textvariable=self.description_var)
        description_entry.grid(
            row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.grid(
            row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        # 存储选中的文件路径
        self.selected_file_path = ""

    def get_student_name(self):
        """获取学生姓名"""
        name = simpledialog.askstring(
            "学生姓名", "请输入您的姓名：", initialvalue=self.student_name
        )
        if name and name.strip():
            self.student_name = name.strip()
            self.student_name_label.config(text=f"学生姓名：{self.student_name}")
        elif not self.student_name:
            # 如果没有输入姓名，显示警告
            messagebox.showwarning("警告", "请设置学生姓名后再使用")
            self.root.after(1000, self.get_student_name)  # 1秒后再次询问

    def change_student_name(self):
        """修改学生姓名"""
        self.get_student_name()

    def connect_teacher(self):
        """手动连接教师端"""
        ip = self.ip_var.get().strip()
        port_text = self.port_var.get().strip()
        if not ip:
            messagebox.showwarning("警告", "请输入教师端IP地址")
            return
        if not port_text.isdigit():
            messagebox.showwarning("警告", "端口必须为数字")
            return
        port = int(port_text)
        self.connection_status_var.set("正在连接...")

        def do_connect():
            try:
                url_base = f"http://{ip}:{port}"
                resp = requests.get(f"{url_base}/api/health", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "ok":
                        self.teacher_ip = ip
                        self.teacher_port = port
                        self.base_url = url_base
                        self.connection_status_var.set(f"已连接: {ip}:{port}")
                        self.refresh_teacher_files()
                        return
                self.connection_status_var.set("连接失败，请确认IP/端口及教师端已启动")
            except Exception as e:
                self.connection_status_var.set(f"连接错误: {e}")

        threading.Thread(target=do_connect, daemon=True).start()

    def get_local_ip(self):
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def refresh_teacher_files(self):
        """刷新老师文件列表"""
        if not self.base_url:
            return

        def load_files():
            try:
                response = requests.get(f"{self.base_url}/api/teacher/files", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        files = data.get("files", [])

                        # 清空现有项目
                        for item in self.teacher_tree.get_children():
                            self.teacher_tree.delete(item)

                        # 添加文件到列表
                        for file_info in files:
                            file_size = self.format_file_size(
                                file_info.get("file_size", 0)
                            )
                            upload_time = file_info.get("upload_time", "")[:19].replace(
                                "T", " "
                            )

                            self.teacher_tree.insert(
                                "",
                                "end",
                                text=file_info.get("filename", ""),
                                values=(file_size, upload_time),
                                tags=(file_info.get("file_id", ""),),
                            )

                        self.status_var.set(f"已加载 {len(files)} 个文件")
                    else:
                        self.status_var.set("获取文件列表失败")
                else:
                    self.status_var.set("连接教师端失败")
            except Exception as e:
                self.status_var.set(f"连接错误: {str(e)}")

        threading.Thread(target=load_files, daemon=True).start()

    def download_file(self):
        """下载老师文件"""
        if not self.student_name:
            messagebox.showwarning("警告", "请先设置学生姓名")
            return

        if not self.base_url:
            messagebox.showwarning("警告", "未连接到教师端")
            return

        selection = self.teacher_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要下载的文件")
            return

        item = self.teacher_tree.item(selection[0])
        file_id = item["tags"][0] if item["tags"] else None
        filename = item["text"]

        if not file_id:
            messagebox.showerror("错误", "无法获取文件ID")
            return

        # 选择保存位置
        save_path = filedialog.asksaveasfilename(
            title="选择保存位置", initialvalue=filename, filetypes=[("所有文件", "*.*")]
        )

        if not save_path:
            return

        def download():
            try:
                self.status_var.set("正在下载文件...")
                response = requests.get(
                    f"{self.base_url}/api/teacher/files/{file_id}", timeout=30
                )

                if response.status_code == 200:
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    messagebox.showinfo("成功", "文件下载成功！")
                else:
                    messagebox.showerror("错误", "下载失败")

                self.status_var.set("就绪")
            except Exception as e:
                messagebox.showerror("错误", f"下载失败：{str(e)}")
                self.status_var.set("就绪")

        threading.Thread(target=download, daemon=True).start()

    def select_work_file(self):
        """选择作业文件"""
        file_path = filedialog.askopenfilename(
            title="选择作业文件", filetypes=[("所有文件", "*.*")]
        )

        if file_path:
            self.selected_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_path_var.set(filename)

    def upload_work(self):
        """上传作业"""
        if not self.student_name:
            messagebox.showwarning("警告", "请先设置学生姓名")
            return

        if not self.base_url:
            messagebox.showwarning("警告", "未连接到教师端")
            return

        if not self.selected_file_path:
            messagebox.showwarning("警告", "请先选择要上传的作业文件")
            return

        if not os.path.exists(self.selected_file_path):
            messagebox.showerror("错误", "选择的文件不存在")
            return

        description = self.description_var.get().strip()

        def upload():
            try:
                self.status_var.set("正在上传作业...")

                with open(self.selected_file_path, "rb") as f:
                    files = {"file": f}
                    data = {
                        "student_name": self.student_name,
                        "description": description,
                    }
                    response = requests.post(
                        f"{self.base_url}/api/student/work",
                        files=files,
                        data=data,
                        timeout=30,
                    )

                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        messagebox.showinfo("成功", "作业上传成功！")
                        # 清空选择
                        self.selected_file_path = ""
                        self.file_path_var.set("未选择文件")
                        self.description_var.set("")
                    else:
                        messagebox.showerror(
                            "错误", f"上传失败：{result.get('error', '未知错误')}"
                        )
                else:
                    messagebox.showerror("错误", "上传失败")

                self.status_var.set("就绪")
            except Exception as e:
                messagebox.showerror("错误", f"上传失败：{str(e)}")
                self.status_var.set("就绪")

        threading.Thread(target=upload, daemon=True).start()

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
    app = StudentApp()
    app.run()
