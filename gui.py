import json
import logging
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from tkinterdnd2 import TkinterDnD, DND_FILES

from core import DataProcessor

# 配置日志系统，设置日志格式和级别
logging.basicConfig(
    format='[%(levelname)s] %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)


class ModernGUI(TkinterDnD.Tk):
    """GUI界面，继承自TkinterDnD.Tk，支持拖拽功能"""

    def __init__(self):
        """初始化GUI界面，设置窗口标题、大小、样式，并初始化UI组件"""
        super().__init__()
        self.title("halo数据批量替换器")
        self.geometry("1000x800")
        self.style = ttk.Style(self)
        self._setup_style()
        self._init_ui()
        self.process_thread = None
        self.message_queue = queue.Queue()
        self.after(100, self.process_messages)

    def _setup_style(self):
        """配置界面样式，包括颜色、字体、按钮、进度条等组件的样式"""
        self.style.theme_use("clam")

        # 主色调配置
        bg_color = "#f8f9fa"
        primary_color = "#007bff"
        success_color = "#28a745"
        text_color = "#212529"

        # 基础样式
        self.style.configure(".",
                             font=("Segoe UI", 10),
                             background=bg_color,
                             foreground=text_color)

        # 框架样式
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabelFrame",
                             background=bg_color,
                             bordercolor="#dee2e6",
                             relief=tk.GROOVE,
                             padding=5)

        # 标签样式
        self.style.configure("TLabel",
                             background=bg_color,
                             font=("Segoe UI", 10))

        # 按钮样式
        self.style.configure("TButton",
                             padding=6,
                             relief=tk.RAISED)
        self.style.map("TButton",
                       foreground=[('active', 'white'), ('!active', 'white')],
                       background=[('active', primary_color), ('!active', primary_color)],
                       relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

        # 进度条样式
        self.style.configure("Horizontal.TProgressbar",
                             thickness=10,
                             troughcolor="#e9ecef",
                             background=success_color,
                             bordercolor="#dee2e6",
                             lightcolor=success_color,
                             darkcolor=success_color)

        # 输入框样式
        self.style.configure("TEntry",
                             fieldbackground="white",
                             bordercolor="#ced4da",
                             lightcolor="#ced4da",
                             darkcolor="#ced4da",
                             padding=5)

    def _init_ui(self):
        """初始化界面组件，包括公告区域、拖拽区域、控制面板、进度条和日志面板"""
        self._create_announcement_panel()
        self._create_drop_zone()
        self._create_control_panel()
        self._create_progress_bar()
        self._create_log_panel()

    def _create_announcement_panel(self):
        """创建公告区域，显示提示信息"""
        announcement_frame = ttk.LabelFrame(
            self,
            text="公告",
            padding=10
        )
        announcement_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        announcement_text = "不保证数据稳定！\n请做好完整的数据备份！"
        ttk.Label(
            announcement_frame,
            text=announcement_text,
            font=("Segoe UI", 10),
            foreground="#495057",
            justify=tk.CENTER,
            wraplength=800
        ).pack(pady=5)

    def _create_drop_zone(self):
        """创建拖拽区域，支持文件拖拽和点击选择文件功能"""
        # 主容器框架
        container = ttk.Frame(self)
        container.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # 标题标签
        title_label = ttk.Label(
            container,
            text="选择文件区域",
            font=("Segoe UI", 10, "bold")
        )
        title_label.pack(anchor=tk.NW)

        # 拖拽区域框架
        drop_frame = tk.Frame(container, bg="#f8f9fa", bd=2, relief=tk.GROOVE)
        # 注册拖拽功能到主窗口
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_file_drop)
        drop_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 添加图标和更醒目的拖拽区域
        self.drop_label = ttk.Label(
            drop_frame,
            text="📁 拖拽文件到此处区域\n或点击此处选择文件",
            font=("Segoe UI", 12),
            wraplength=400,
            anchor=tk.CENTER,
            foreground="#495057",
            justify=tk.CENTER,
            background="#f8f9fa"
        )
        self.drop_label.pack(expand=True, fill=tk.BOTH, padx=30, pady=50)

        # 绑定点击事件来选择文件
        self.drop_label.bind("<Button-1>", lambda e: self._select_file())
        drop_frame.bind("<Button-1>", lambda e: self._select_file())

    def _create_control_panel(self):
        """创建控制面板，包括输入参数和输出设置"""
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill=tk.X, padx=20, pady=15)

        # 输入参数区域
        input_frame = ttk.LabelFrame(control_frame, text="处理参数", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        ttk.Label(input_frame, text="搜索内容:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.search_entry = ttk.Entry(input_frame, width=45, font=("Segoe UI", 10))
        self.search_entry.grid(row=0, column=1, padx=10, pady=3)

        ttk.Label(input_frame, text="替换内容:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.replace_entry = ttk.Entry(input_frame, width=45, font=("Segoe UI", 10))
        self.replace_entry.grid(row=1, column=1, padx=10, pady=3)

        # 输出设置区域（单行布局）
        output_frame = ttk.LabelFrame(control_frame, text="输出设置", padding=10)
        output_frame.grid(row=0, column=1, padx=10, pady=5, sticky=tk.E)

        # 输出目录选择按钮
        output_btn = ttk.Button(
            output_frame,
            text="📁 输出目录",
            command=self._select_output_dir,
            style="Accent.TButton",
            width=12
        )
        output_btn.pack(side=tk.LEFT, padx=5)

        # 输出路径显示
        self.output_path = tk.StringVar()

        # 操作按钮
        self.process_btn = ttk.Button(
            output_frame,
            text="▶ 解码",
            command=self.start_decoding,
            style="Success.TButton",
            width=8
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)

        self.replace_btn = ttk.Button(
            output_frame,
            text="🔍 替换",
            command=self.start_replacing,
            style="Accent.TButton",
            width=8
        )
        self.replace_btn.pack(side=tk.LEFT, padx=5)

        self.reencode_btn = ttk.Button(
            output_frame,
            text="🔒 加密",
            command=self.start_reencoding,
            style="Accent.TButton",
            width=8
        )
        self.reencode_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(
            output_frame,
            text="💾 保存",
            command=self.save_processed_data,
            style="Accent.TButton",
            width=8,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

    def _create_progress_bar(self):
        """创建进度条，用于显示处理进度"""
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, padx=20, pady=15)

        ttk.Label(
            progress_frame,
            text="处理进度:",
            font=("Segoe UI", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode='determinate',
            style="Horizontal.TProgressbar"
        )
        self.progress.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def _create_log_panel(self):
        """创建日志面板，用于显示处理日志"""
        log_frame = ttk.LabelFrame(self, text="处理日志", padding=10)
        log_frame.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)

        # 添加工具栏
        toolbar = ttk.Frame(log_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(
            toolbar,
            text="清空日志",
            command=lambda: [self.log_text.config(state=tk.NORMAL),
                             self.log_text.delete(1.0, tk.END),
                             self.log_text.config(state=tk.DISABLED)],
            style="Small.TButton"
        ).pack(side=tk.LEFT)

        ttk.Button(
            toolbar,
            text="复制日志",
            command=lambda: self.clipboard_clear() or
                            self.clipboard_append(self.log_text.get(1.0, tk.END)),
            style="Small.TButton"
        ).pack(side=tk.LEFT, padx=5)

        # 日志文本框
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=10,
            font=("Consolas", 9),
            bg="white",
            padx=5,
            pady=5,
            insertbackground="black"
        )

        # 滚动条
        scrollbar = ttk.Scrollbar(
            log_frame,
            command=self.log_text.yview,
            style="Vertical.TScrollbar"
        )
        self.log_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log_message(self, message: str, level: str = "info"):
        """记录日志信息，支持不同级别的日志显示不同颜色"""
        color_map = {
            "info": "black",
            "warning": "orange",
            "error": "red"
        }
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(
            tk.END,
            message + "\n",
            (level,)
        )
        self.log_text.tag_config("info", foreground="black")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def process_messages(self):
        """处理消息队列，将队列中的消息显示在日志面板中"""
        while not self.message_queue.empty():
            try:
                msg, level = self.message_queue.get_nowait()
                self.log_message(msg, level)
            except queue.Empty:
                break
        self.after(100, self.process_messages)

    def _on_file_drop(self, event):
        """处理文件拖放事件，获取拖拽的文件路径"""
        files = [f.strip("{}") for f in self.tk.splitlist(event.data)]
        if files:
            self.file_path = files[0]
            self._update_ui(f"已选择文件: {os.path.basename(self.file_path)}")

    def _select_file(self):
        """选择输入文件，通过文件对话框获取文件路径"""
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Data和JSON文件", "*.data *.json"), ("所有文件", "*.*")]
        )
        if self.file_path:
            self._update_ui(f"已选择文件: {os.path.basename(self.file_path)}")

    def _select_output_dir(self):
        """选择输出目录，通过文件对话框获取目录路径"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.set(directory)
            self.log_message(f"输出目录设置为: {directory}")

    def _update_ui(self, message: str):
        """更新界面状态，显示当前选择的文件路径并重置进度条"""
        self.drop_label.config(text=message)
        self.progress["value"] = 0

    def start_decoding(self):
        """启动解码流程，检查输入文件是否存在，并启动解码线程"""
        if not hasattr(self, 'file_path') or not self.file_path:
            self.show_error("请先选择输入文件")
            return

        output_dir = self.output_path.get() or os.path.dirname(self.file_path)
        output_name = f"decoded_{os.path.basename(self.file_path)}"
        output_path = os.path.join(output_dir, output_name)

        self.process_btn.config(state=tk.DISABLED)
        self.replace_btn.config(state=tk.DISABLED)
        self.reencode_btn.config(state=tk.DISABLED)
        self.log_message("开始解码文件...", "info")

        self.process_thread = threading.Thread(
            target=self._run_decoding,
            args=(self.file_path, output_path),
            daemon=True
        )
        self.process_thread.start()

    def start_replacing(self):
        """启动替换流程，检查输入文件是否存在，并启动替换线程"""
        if not hasattr(self, 'file_path') or not self.file_path:
            self.show_error("请先选择输入文件")
            return

        search_str = self.search_entry.get()
        replace_str = self.replace_entry.get()

        if not search_str:
            self.show_error("请输入搜索内容")
            return

        output_dir = self.output_path.get() or os.path.dirname(self.file_path)
        output_name = f"replaced_{os.path.basename(self.file_path)}"
        output_path = os.path.join(output_dir, output_name)

        self.process_btn.config(state=tk.DISABLED)
        self.replace_btn.config(state=tk.DISABLED)
        self.reencode_btn.config(state=tk.DISABLED)
        self.log_message("开始替换文件内容...", "info")

        self.process_thread = threading.Thread(
            target=self._run_replacing,
            args=(self.file_path, output_path, search_str, replace_str),
            daemon=True
        )
        self.process_thread.start()

    def start_reencoding(self):
        """启动重新加密流程，检查输入文件是否存在，并启动重新加密线程"""
        if not hasattr(self, 'file_path') or not self.file_path:
            self.show_error("请先选择解码副本文件")
            return

        output_dir = self.output_path.get() or os.path.dirname(self.file_path)
        # 获取原始文件名（不带后缀）并添加固定.data后缀
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        output_name = f"reencoded_{base_name}.data"
        output_path = os.path.join(output_dir, output_name)

        self.process_btn.config(state=tk.DISABLED)
        self.reencode_btn.config(state=tk.DISABLED)
        self.log_message("开始重新加密文件...", "info")

        self.process_thread = threading.Thread(
            target=self._run_reencoding,
            args=(self.file_path, output_path),
            daemon=True
        )
        self.process_thread.start()

    def _run_decoding(self, input_path: str, output_path: str):
        """执行解码过程，调用DataProcessor解码文件内容"""
        try:
            self.original_data = DataProcessor.decode_file(input_path)
            self.processed_data = self.original_data
            self.message_queue.put((
                "解码完成！请点击保存按钮保存结果",
                "info"
            ))
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.message_queue.put((
                f"解码失败: {str(e)}",
                "error"
            ))
        finally:
            self.process_btn.config(state=tk.NORMAL)
            self.replace_btn.config(state=tk.NORMAL)
            self.reencode_btn.config(state=tk.NORMAL)
            self.progress["value"] = 100

    def _run_replacing(self, input_path: str, output_path: str, search: str, replace: str):
        """执行替换过程，调用DataProcessor替换文件内容"""
        try:
            self.original_data, self.processed_data = DataProcessor.replace_content_in_file(input_path, search, replace)
            self.message_queue.put((
                "替换完成！请点击保存按钮保存结果",
                "info"
            ))
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.message_queue.put((
                f"替换失败: {str(e)}",
                "error"
            ))
        finally:
            self.process_btn.config(state=tk.NORMAL)
            self.replace_btn.config(state=tk.NORMAL)
            self.reencode_btn.config(state=tk.NORMAL)
            self.progress["value"] = 100

    def save_processed_data(self):
        """保存处理后的数据到文件"""
        if not hasattr(self, 'processed_data') and not hasattr(self, 'reencoded_data'):
            self.show_error("没有可保存的数据，请先解码或加密文件")
            return

        output_dir = self.output_path.get() or os.path.dirname(self.file_path)
        output_name = f"processed_{os.path.basename(self.file_path)}"
        output_path = os.path.join(output_dir, output_name)

        try:
            if hasattr(self, 'reencoded_data'):
                # 保存加密数据
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(self.reencoded_data, f, ensure_ascii=False, indent=2)
                self.message_queue.put((
                    f"加密数据保存成功！\n输出文件: {output_path}",
                    "info"
                ))
            else:
                # 保存处理后的数据
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(self.processed_data, f, ensure_ascii=False, indent=2)
                decoded_path = DataProcessor.save_decoded_copy(self.original_data, output_path)
                self.message_queue.put((
                    f"保存成功！\n输出文件: {output_path}\n解码副本: {decoded_path}",
                    "info"
                ))
            
            self.save_btn.config(state=tk.DISABLED)
        except Exception as e:
            self.message_queue.put((
                f"保存失败: {str(e)}",
                "error"
            ))

    def _run_reencoding(self, input_path: str, output_path: str):
        """执行重新加密过程，调用DataProcessor重新加密数据但不保存"""
        try:
            self.reencoded_data = DataProcessor.reencode_data(input_path)
            self.message_queue.put((
                "加密完成！请点击保存按钮保存结果",
                "info"
            ))
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.message_queue.put((
                f"加密失败: {str(e)}",
                "error"
            ))
        finally:
            self.process_btn.config(state=tk.NORMAL)
            self.reencode_btn.config(state=tk.NORMAL)
            self.progress["value"] = 100

    def show_error(self, message: str):
        """显示错误提示，弹出错误对话框并记录错误日志"""
        messagebox.showerror("错误", message)
        self.log_message(f"错误: {message}", "error")


if __name__ == "__main__":
    app = ModernGUI()
    app.mainloop()
