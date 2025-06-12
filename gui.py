import json
import logging
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from tkinterdnd2 import TkinterDnD, DND_FILES

from core import DataProcessor

# 配置日志系统
logging.basicConfig(
    format='[%(levelname)s] %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)


class ModernGUI(TkinterDnD.Tk):
    """GUI界面，继承自TkinterDnD.Tk，支持拖拽功能"""

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_style()
        self._init_variables()
        self._init_ui()
        self._init_threads_and_queue()
        self.after(100, self.process_messages)

    # ====== 界面结构与初始化 ======
    def _setup_window(self):
        self.title("halo数据批量替换器")
        self.geometry("1000x800")

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # 主色调
        bg_color = "#f8f9fa"
        primary_color = "#007bff"
        success_color = "#28a745"
        text_color = "#212529"

        style.configure(".", font=("Segoe UI", 10), background=bg_color, foreground=text_color)
        style.configure("TFrame", background=bg_color)
        style.configure("TLabelFrame", background=bg_color, bordercolor="#dee2e6", relief=tk.GROOVE, padding=5)
        style.configure("TLabel", background=bg_color, font=("Segoe UI", 10))
        style.configure("TButton", padding=6, relief=tk.RAISED)
        style.map("TButton",
                  foreground=[('active', 'white'), ('!active', 'white')],
                  background=[('active', primary_color), ('!active', primary_color)],
                  relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        style.configure("Horizontal.TProgressbar",
                        thickness=10, troughcolor="#e9ecef", background=success_color,
                        bordercolor="#dee2e6", lightcolor=success_color, darkcolor=success_color)
        style.configure("TEntry", fieldbackground="white", bordercolor="#ced4da",
                        lightcolor="#ced4da", darkcolor="#ced4da", padding=5)
        self.style = style

    def _init_variables(self):
        self.file_path = ""
        self.output_path = tk.StringVar()
        self.original_data = None
        self.processed_data = None
        self.reencoded_data = None

    def _init_threads_and_queue(self):
        self.process_thread = None
        self.message_queue = queue.Queue()

    def _init_ui(self):
        self._create_announcement_panel()
        self._create_drop_zone()
        self._create_control_panel()
        self._create_progress_bar()
        self._create_log_panel()

    # ====== 组件创建 ======
    def _create_announcement_panel(self):
        frame = ttk.LabelFrame(self, text="公告", padding=10)
        frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        announcement_text = "不保证数据稳定！\n请做好完整的数据备份！"
        ttk.Label(frame, text=announcement_text, font=("Segoe UI", 10),
                  foreground="#495057", justify=tk.CENTER, wraplength=800).pack(pady=5)

    def _create_drop_zone(self):
        container = ttk.Frame(self)
        container.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        ttk.Label(container, text="选择文件区域", font=("Segoe UI", 10, "bold")).pack(anchor=tk.NW)

        drop_frame = tk.Frame(container, bg="#f8f9fa", bd=2, relief=tk.GROOVE)
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_file_drop)
        drop_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

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
        self.drop_label.bind("<Button-1>", lambda e: self._select_file())
        drop_frame.bind("<Button-1>", lambda e: self._select_file())

    def _create_control_panel(self):
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill=tk.X, padx=20, pady=15)

        # 输入参数
        input_frame = ttk.LabelFrame(control_frame, text="处理参数", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(input_frame, text="搜索内容:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.search_entry = ttk.Entry(input_frame, width=45, font=("Segoe UI", 10))
        self.search_entry.grid(row=0, column=1, padx=10, pady=3)
        ttk.Label(input_frame, text="替换内容:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.replace_entry = ttk.Entry(input_frame, width=45, font=("Segoe UI", 10))
        self.replace_entry.grid(row=1, column=1, padx=10, pady=3)

        # 输出设置
        output_frame = ttk.LabelFrame(control_frame, text="输出设置", padding=10)
        output_frame.grid(row=0, column=1, padx=10, pady=5, sticky=tk.E)

        output_btn = ttk.Button(
            output_frame, text="📁 输出目录",
            command=self._select_output_dir, style="Accent.TButton", width=12
        )
        output_btn.pack(side=tk.LEFT, padx=5)

        # 操作按钮
        self.process_btn = ttk.Button(
            output_frame, text="▶ 解码",
            command=self.start_decoding, style="Success.TButton", width=8
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)

        self.replace_btn = ttk.Button(
            output_frame, text="🔍 替换",
            command=self.start_replacing, style="Accent.TButton", width=8
        )
        self.replace_btn.pack(side=tk.LEFT, padx=5)

        self.reencode_btn = ttk.Button(
            output_frame, text="🔒 编码",
            command=self.start_reencoding, style="Accent.TButton", width=8
        )
        self.reencode_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(
            output_frame, text="💾 保存",
            command=self.save_processed_data, style="Accent.TButton", width=8, state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

    def _create_progress_bar(self):
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, padx=20, pady=15)
        ttk.Label(progress_frame, text="处理进度:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.progress = ttk.Progressbar(
            progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate', style="Horizontal.TProgressbar"
        )
        self.progress.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def _create_log_panel(self):
        log_frame = ttk.LabelFrame(self, text="处理日志", padding=10)
        log_frame.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)
        toolbar = ttk.Frame(log_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(toolbar, text="清空日志",
                   command=self._clear_log, style="Small.TButton").pack(side=tk.LEFT)
        ttk.Button(toolbar, text="复制日志",
                   command=self._copy_log, style="Small.TButton").pack(side=tk.LEFT, padx=5)

        self.log_text = tk.Text(
            log_frame, wrap=tk.WORD, state=tk.DISABLED, height=10,
            font=("Consolas", 9), bg="white", padx=5, pady=5, insertbackground="black"
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview, style="Vertical.TScrollbar")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    # ====== 日志方法区 ======
    def log_message(self, message: str, level: str = "info"):
        color_map = {"info": "black", "warning": "orange", "error": "red"}
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", (level,))
        for lvl, color in color_map.items():
            self.log_text.tag_config(lvl, foreground=color)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _copy_log(self):
        self.clipboard_clear()
        self.clipboard_append(self.log_text.get(1.0, tk.END))

    def process_messages(self):
        while not self.message_queue.empty():
            try:
                msg, level = self.message_queue.get_nowait()
                self.log_message(msg, level)
            except queue.Empty:
                break
        self.after(100, self.process_messages)

    # ====== 文件与UI操作 ======
    def _on_file_drop(self, event):
        files = [f.strip("{}") for f in self.tk.splitlist(event.data)]
        if files:
            self.file_path = files[0]
            self._update_ui(f"已选择文件: {os.path.basename(self.file_path)}")

    def _select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Data和JSON文件", "*.data *.json"), ("所有文件", "*.*")]
        )
        if path:
            self.file_path = path
            self._update_ui(f"已选择文件: {os.path.basename(self.file_path)}")

    def _select_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.set(directory)
            self.log_message(f"输出目录设置为: {directory}")

    def _update_ui(self, message: str):
        self.drop_label.config(text=message)
        self.progress["value"] = 0

    # ====== 主业务流程入口 ======
    def _check_unsaved_data(self) -> bool:
        """检查是否有未保存的数据，返回True表示可以继续操作"""
        if not (self.processed_data or self.reencoded_data):
            return True
            
        answer = messagebox.askyesnocancel(
            "未保存的数据",
            "检测到未保存的前任务数据，是否保存？\n"
            "点击'是'保存，'否'清空数据，'取消'中止操作"
        )
        
        if answer is None:  # 用户点击取消
            return False
        elif answer:  # 用户点击是
            self.save_processed_data()
        else:  # 用户点击否
            self.processed_data = None
            self.reencoded_data = None
            self.save_btn.config(state=tk.DISABLED)
        return True

    def start_decoding(self):
        if not self.file_path:
            self.show_error("请先选择输入文件")
            return
        if not self._check_unsaved_data():
            return
        output_dir = self.output_path.get() or os.path.dirname(self.file_path)
        output_name = f"decoded_{os.path.basename(self.file_path)}"
        output_path = os.path.join(output_dir, output_name)
        self._disable_buttons()
        self.log_message("开始解码文件...", "info")
        self.process_thread = threading.Thread(
            target=self._run_decoding, args=(self.file_path, output_path), daemon=True
        )
        self.process_thread.start()

    def start_replacing(self):
        if not self.file_path:
            self.show_error("请先选择输入文件")
            return
        if not self._check_unsaved_data():
            return
        search_str = self.search_entry.get()
        replace_str = self.replace_entry.get()
        if not search_str:
            self.show_error("请输入搜索内容")
            return
        output_dir = self.output_path.get() or os.path.dirname(self.file_path)
        output_name = f"replaced_{os.path.basename(self.file_path)}"
        output_path = os.path.join(output_dir, output_name)
        self._disable_buttons()
        self.log_message("开始替换文件内容...", "info")
        self.process_thread = threading.Thread(
            target=self._run_replacing,
            args=(self.file_path, output_path, search_str, replace_str),
            daemon=True
        )
        self.process_thread.start()

    def start_reencoding(self):
        if not self.file_path:
            self.show_error("请先选择解码副本文件")
            return
        if not self._check_unsaved_data():
            return
        output_dir = self.output_path.get() or os.path.dirname(self.file_path)
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        output_name = f"reencoded_{base_name}.data"
        output_path = os.path.join(output_dir, output_name)
        self._disable_buttons(reencode_only=True)
        self.log_message("开始重新编码文件...", "info")
        self.process_thread = threading.Thread(
            target=self._run_reencoding, args=(self.file_path, output_path), daemon=True
        )
        self.process_thread.start()

    def save_processed_data(self):
        if not (self.processed_data or self.reencoded_data):
            self.show_error("没有可保存的数据，请先解码或编码文件")
            return
        output_dir = self.output_path.get() or os.path.dirname(self.file_path)
        output_name = f"processed_{os.path.basename(self.file_path)}"
        output_path = os.path.join(output_dir, output_name)
        try:
            if self.reencoded_data:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(self.reencoded_data, f, ensure_ascii=False, indent=2)
                self.message_queue.put((f"编码数据保存成功！\n输出文件: {output_path}", "info"))
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(self.processed_data, f, ensure_ascii=False, indent=2)
                if self.original_data:
                    decoded_path = DataProcessor.save_decoded_copy(self.original_data, output_path)
                    self.message_queue.put((f"保存成功！\n输出文件: {output_path}\n解码副本: {decoded_path}", "info"))
                else:
                    self.message_queue.put((f"保存成功！\n输出文件: {output_path}", "info"))
            self.save_btn.config(state=tk.DISABLED)
        except Exception as e:
            self.message_queue.put((f"保存失败: {str(e)}", "error"))

    # ====== 后台处理方法区 ======
    def _run_decoding(self, input_path: str, output_path: str):
        try:
            self.original_data = DataProcessor.decode_file(input_path)
            self.processed_data = self.original_data
            self.message_queue.put(("解码完成！请点击保存按钮保存结果", "info"))
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.message_queue.put((f"解码失败: {str(e)}", "error"))
        finally:
            self._enable_buttons()

    def _run_replacing(self, input_path: str, output_path: str, search: str, replace: str):
        try:
            self.original_data, self.processed_data = DataProcessor.replace_content_in_file(input_path, search, replace)
            self.message_queue.put(("替换完成！请点击保存按钮保存结果", "info"))
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.message_queue.put((f"替换失败: {str(e)}", "error"))
        finally:
            self._enable_buttons()

    def _run_reencoding(self, input_path: str, output_path: str):
        try:
            self.reencoded_data = DataProcessor.reencode_data(input_path)
            self.message_queue.put(("编码完成！请点击保存按钮保存结果", "info"))
            self.save_btn.config(state=tk.NORMAL)
        except ValueError as e:
            if "编码功能只支持JSON文件" in str(e):
                self.message_queue.put(("编码功能只对.json文件生效", "error"))
                self.show_error("编码功能只对.json文件生效")
            else:
                self.message_queue.put((f"编码失败: {str(e)}", "error"))
                self.show_error(f"编码失败: {str(e)}")
        except Exception as e:
            self.message_queue.put((f"编码失败: {str(e)}", "error"))
            self.show_error(f"编码失败: {str(e)}")
        finally:
            self._enable_buttons(reencode_only=True)

    # ====== 按钮状态管理 ======
    def _disable_buttons(self, reencode_only=False):
        self.process_btn.config(state=tk.DISABLED)
        self.replace_btn.config(state=tk.DISABLED)
        self.reencode_btn.config(state=tk.DISABLED)
        if not reencode_only:
            self.save_btn.config(state=tk.DISABLED)
        self.progress["value"] = 0

    def _enable_buttons(self, reencode_only=False):
        self.process_btn.config(state=tk.NORMAL)
        self.replace_btn.config(state=tk.NORMAL)
        self.reencode_btn.config(state=tk.NORMAL)
        if not reencode_only:
            self.save_btn.config(state=tk.NORMAL)
        self.progress["value"] = 100

    # ====== 错误弹窗 ======
    def show_error(self, message: str):
        messagebox.showerror("错误", message)
        self.log_message(f"错误: {message}", "error")


if __name__ == "__main__":
    app = ModernGUI()
    app.mainloop()
