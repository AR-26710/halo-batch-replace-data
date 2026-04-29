from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

from di.container import configure_container, get_use_cases
from modules.application.use_cases.batch_replace_use_case import BatchReplaceInput
from modules.application.use_cases.export_extensions_use_case import ExportExtensionsInput
from modules.application.use_cases.load_extensions_use_case import LoadExtensionsInput
from modules.core.logging.logger import setup_logging
from modules.infrastructure.types.replace_types import ReplaceRule, ReplaceScope
from modules.presentation.gui.theme import ThemeManager
from modules.presentation.gui.components.header import HeaderFrame
from modules.presentation.gui.components.warning_banner import WarningBannerFrame
from modules.presentation.gui.components.drop_zone import DropZoneFrame
from modules.presentation.gui.components.params_actions import ParamsActionsFrame
from modules.presentation.gui.components.search_scope import SearchScopeFrame
from modules.presentation.gui.components.log_panel import LogPanelFrame

setup_logging()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ModernGUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self._container = configure_container()
        self._use_cases = get_use_cases(self._container)
        self._theme = ThemeManager()
        self._init_variables()
        self._setup_window()
        self._init_ui()
        self._init_threads_and_queue()
        self.after(100, self.process_messages)

    def _setup_window(self):
        self.title("Halo 数据批量替换器")
        self.geometry("960x780")
        self.minsize(800, 650)
        self.configure(bg=self._theme.get_bg_color())
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self._on_file_drop)

    def _init_variables(self):
        self.file_path = ""
        self.original_data = None
        self.processed_data = None
        self.reencoded_data = None

    def _init_threads_and_queue(self):
        self.process_thread = None
        self.message_queue = queue.Queue()

    def _init_ui(self):
        self._header = HeaderFrame(self, self._theme, on_toggle_appearance=self._toggle_appearance)
        self._theme.add_listener(self._header)

        self._scrollable = ctk.CTkScrollableFrame(
            self,
            fg_color=self._theme.bg(),
            corner_radius=0,
            scrollbar_button_color=self._theme.border(),
            scrollbar_button_hover_color=self._theme.sub_text(),
        )
        self._scrollable.pack(fill=ctk.BOTH, expand=True)

        self._warning_banner = WarningBannerFrame(self._scrollable, self._theme)
        self._theme.add_listener(self._warning_banner)

        self._drop_zone = DropZoneFrame(self._scrollable, self._theme, on_select_file=self._select_file)
        self._theme.add_listener(self._drop_zone)

        self._params_actions = ParamsActionsFrame(
            self._scrollable,
            self._theme,
            on_select_output_dir=self._select_output_dir,
            on_decode=self.start_decoding,
            on_replace=self.start_replacing,
            on_reencode=self.start_reencoding,
            on_save=self.save_processed_data,
        )
        self._theme.add_listener(self._params_actions)

        self._search_scope = SearchScopeFrame(self._scrollable, self._theme)
        self._theme.add_listener(self._search_scope)

        self._log_panel = LogPanelFrame(self._scrollable, self._theme)
        self._theme.add_listener(self._log_panel)

    def _toggle_appearance(self):
        self._theme.toggle_appearance()
        self.configure(bg=self._theme.get_bg_color())
        self._theme.refresh_all()

    def process_messages(self):
        while not self.message_queue.empty():
            try:
                msg, level = self.message_queue.get_nowait()
                self._log_panel.log_message(msg, level)
            except queue.Empty:
                break
        self.after(100, self.process_messages)

    def _on_file_drop(self, event):
        files = [f.strip("{}") for f in self.tk.splitlist(event.data)]
        if files:
            self.file_path = files[0]
            self._update_ui(f"✅  已选择文件: {os.path.basename(self.file_path)}")
            self._auto_load_file()

    def _select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Data和JSON文件", "*.data *.json"), ("所有文件", "*.*")]
        )
        if path:
            self.file_path = path
            self._update_ui(f"✅  已选择文件: {os.path.basename(self.file_path)}")
            self._auto_load_file()

    def _auto_load_file(self):
        self._log_panel.log_message("正在加载文件...", "info")
        self.process_thread = threading.Thread(
            target=self._run_auto_load, args=(self.file_path,), daemon=True
        )
        self.process_thread.start()

    def _run_auto_load(self, input_path: str):
        try:
            load_result = self._use_cases["load"].execute(
                LoadExtensionsInput(filepath=input_path)
            )
            if load_result.success:
                repo = self._use_cases["extension_repo"]
                kinds = repo.get_kinds()
                self.after(0, lambda: self._search_scope.update_kinds(kinds))
                self.message_queue.put(
                    (f"文件加载完成！共 {load_result.count} 条记录，{len(kinds)} 种类型", "success")
                )
            else:
                self.message_queue.put((f"文件加载失败: {load_result.error}", "error"))
        except Exception as e:
            self.message_queue.put((f"文件加载失败: {str(e)}", "error"))

    def _select_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self._params_actions.set_output_dir(directory)
            self._log_panel.log_message(f"输出目录设置为: {directory}")

    def _update_ui(self, message: str):
        self._drop_zone.update_message(message)

    def _check_unsaved_data(self) -> bool:
        if not (self.processed_data or self.reencoded_data):
            return True

        answer = messagebox.askyesnocancel(
            "未保存的数据",
            "检测到未保存的前任务数据，是否保存？\n"
            "点击'是'保存，'否'清空数据，'取消'中止操作",
        )

        if answer is None:
            return False
        elif answer:
            self.save_processed_data()
        else:
            self.processed_data = None
            self.reencoded_data = None
            self._params_actions.disable_save_button()
        return True

    def start_decoding(self):
        if not self.file_path:
            self.show_error("请先选择输入文件")
            return
        if not self._check_unsaved_data():
            return
        self._params_actions.disable_buttons()
        self._log_panel.log_message("开始解码文件...", "info")
        self.process_thread = threading.Thread(
            target=self._run_decoding, args=(self.file_path,), daemon=True
        )
        self.process_thread.start()

    def start_replacing(self):
        if not self.file_path:
            self.show_error("请先选择输入文件")
            return
        if not self._check_unsaved_data():
            return
        search_str = self._params_actions.get_search_text()
        replace_str = self._params_actions.get_replace_text()
        if not search_str:
            self.show_error("请输入搜索内容")
            return
        is_regex = self._params_actions.is_regex()
        scope = self._search_scope.get_scope()
        self._params_actions.disable_buttons()
        self._log_panel.log_message("开始替换文件内容...", "info")
        self.process_thread = threading.Thread(
            target=self._run_replacing,
            args=(self.file_path, search_str, replace_str, is_regex, scope),
            daemon=True,
        )
        self.process_thread.start()

    def start_reencoding(self):
        if not self.file_path:
            self.show_error("请先选择解码副本文件")
            return
        if not self._check_unsaved_data():
            return
        self._params_actions.disable_buttons(reencode_only=True)
        self._log_panel.log_message("开始重新编码文件...", "info")
        self.process_thread = threading.Thread(
            target=self._run_reencoding, args=(self.file_path,), daemon=True
        )
        self.process_thread.start()

    def save_processed_data(self):
        if not (self.processed_data or self.reencoded_data):
            self.show_error("没有可保存的数据，请先解码或编码文件")
            return
        output_dir = self._params_actions.get_output_dir() or os.path.dirname(self.file_path)
        try:
            if self.reencoded_data:
                output_name = f"reencoded_{os.path.basename(self.file_path)}"
                base_path, _ = os.path.splitext(os.path.join(output_dir, output_name))
                data_path = f"{base_path}.data"
                export_result = self._use_cases["export"].execute(
                    ExportExtensionsInput(filepath=data_path)
                )
                if export_result.success:
                    self.message_queue.put(
                        (f"编码数据保存成功！\n输出文件: {data_path}", "success")
                    )
                else:
                    self.message_queue.put((f"保存失败: {export_result.error}", "error"))
            else:
                output_name = f"processed_{os.path.basename(self.file_path)}"
                output_path = os.path.join(output_dir, output_name)
                export_result = self._use_cases["export"].execute(
                    ExportExtensionsInput(filepath=output_path)
                )
                if export_result.success:
                    self.message_queue.put(
                        (f"保存成功！\n输出文件: {output_path}", "success")
                    )
                else:
                    self.message_queue.put((f"保存失败: {export_result.error}", "error"))
            self._params_actions.disable_save_button()
        except Exception as e:
            self.message_queue.put((f"保存失败: {str(e)}", "error"))

    def _run_decoding(self, input_path: str):
        try:
            load_result = self._use_cases["load"].execute(
                LoadExtensionsInput(filepath=input_path)
            )
            if load_result.success:
                self.original_data = True
                self.processed_data = True
                repo = self._use_cases["extension_repo"]
                kinds = repo.get_kinds()
                self.after(0, lambda: self._search_scope.update_kinds(kinds))
                self.message_queue.put(
                    (f"解码完成！共 {load_result.count} 条记录。请点击保存按钮保存结果", "success")
                )
                self._params_actions.enable_save_button()
            else:
                self.message_queue.put((f"解码失败: {load_result.error}", "error"))
        except Exception as e:
            self.message_queue.put((f"解码失败: {str(e)}", "error"))
        finally:
            self._params_actions.enable_buttons()

    def _run_replacing(self, input_path: str, search: str, replace: str, is_regex: bool, scope: ReplaceScope):
        try:
            load_result = self._use_cases["load"].execute(
                LoadExtensionsInput(filepath=input_path)
            )
            if not load_result.success:
                self.message_queue.put((f"加载文件失败: {load_result.error}", "error"))
                return

            replace_result = self._use_cases["batch_replace"].execute(
                BatchReplaceInput(
                    rules=[ReplaceRule(search=search, replace=replace, is_regex=is_regex)],
                    scope=scope,
                )
            )
            if replace_result.success:
                self.original_data = True
                self.processed_data = True
                self.message_queue.put(
                    (
                        f"替换完成！更新了 {replace_result.updated_count} 条记录。请点击保存按钮保存结果",
                        "success",
                    )
                )
                self._params_actions.enable_save_button()
            else:
                self.message_queue.put((f"替换失败: {replace_result.error}", "error"))
        except Exception as e:
            self.message_queue.put((f"替换失败: {str(e)}", "error"))
        finally:
            self._params_actions.enable_buttons()
    def _run_reencoding(self, input_path: str):
        try:
            load_result = self._use_cases["load"].execute(
                LoadExtensionsInput(filepath=input_path)
            )
            if not load_result.success:
                self.message_queue.put((f"加载文件失败: {load_result.error}", "error"))
                return

            self.reencoded_data = True
            self.message_queue.put(("编码完成！请点击保存按钮保存结果", "success"))
            self._params_actions.enable_save_button()
        except Exception as e:
            self.message_queue.put((f"编码失败: {str(e)}", "error"))
        finally:
            self._params_actions.enable_buttons(reencode_only=True)

    def show_error(self, message: str):
        messagebox.showerror("错误", message)
        self._log_panel.log_message(f"错误: {message}", "error")


if __name__ == "__main__":
    app = ModernGUI()
    app.mainloop()
