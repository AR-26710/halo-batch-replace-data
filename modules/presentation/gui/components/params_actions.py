from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from modules.presentation.gui.theme import ThemeManager


class ParamsActionsFrame(ctk.CTkFrame):
    def __init__(self, master, theme: ThemeManager, on_select_output_dir, on_decode, on_replace, on_reencode, on_save, **kwargs):
        super().__init__(master, fg_color=theme.bg(), **kwargs)
        self.pack(fill=ctk.X, padx=20, pady=(12, 0))

        self._theme = theme
        self.output_path = tk.StringVar()

        self._build_params_card(theme)
        self._build_actions_card(theme, on_select_output_dir, on_decode, on_replace, on_reencode, on_save)

    def _build_params_card(self, theme: ThemeManager):
        params_card = ctk.CTkFrame(self, fg_color=theme.card(), corner_radius=12)
        params_card._card_type = True
        params_card.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(0, 8))

        params_title = ctk.CTkLabel(
            params_card,
            text="处理参数",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=theme.text(),
        )
        params_title.pack(anchor=tk.W, padx=20, pady=(16, 8))

        search_frame = ctk.CTkFrame(params_card, fg_color="transparent")
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 6))

        ctk.CTkLabel(
            search_frame,
            text="搜索内容",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color=theme.sub_text(),
            width=70,
        ).pack(side=tk.LEFT, padx=(0, 8))
        self.search_entry = ctk.CTkEntry(
            search_frame,
            height=38,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            placeholder_text="输入要搜索的内容...",
            corner_radius=8,
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        replace_frame = ctk.CTkFrame(params_card, fg_color="transparent")
        replace_frame.pack(fill=tk.X, padx=20, pady=(0, 16))

        ctk.CTkLabel(
            replace_frame,
            text="替换内容",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color=theme.sub_text(),
            width=70,
        ).pack(side=tk.LEFT, padx=(0, 8))
        self.replace_entry = ctk.CTkEntry(
            replace_frame,
            height=38,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            placeholder_text="输入要替换的内容...",
            corner_radius=8,
        )
        self.replace_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        regex_frame = ctk.CTkFrame(params_card, fg_color="transparent")
        regex_frame.pack(fill=tk.X, padx=20, pady=(0, 16))

        self.is_regex_var = tk.BooleanVar(value=True)
        self.regex_checkbox = ctk.CTkCheckBox(
            regex_frame,
            text="使用正则表达式",
            variable=self.is_regex_var,
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color=theme.text(),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
        )
        self.regex_checkbox.pack(side=tk.LEFT)

    def _build_actions_card(self, theme: ThemeManager, on_select_output_dir, on_decode, on_replace, on_reencode, on_save):
        actions_card = ctk.CTkFrame(self, fg_color=theme.card(), corner_radius=12, width=320)
        actions_card._card_type = True
        actions_card.pack(side=ctk.RIGHT, fill=tk.Y, padx=(8, 0))
        actions_card.pack_propagate(False)

        actions_title = ctk.CTkLabel(
            actions_card,
            text="操作",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=theme.text(),
        )
        actions_title.pack(anchor=tk.W, padx=20, pady=(16, 10))

        btn_row1 = ctk.CTkFrame(actions_card, fg_color="transparent")
        btn_row1.pack(fill=tk.X, padx=16, pady=(0, 6))

        self.output_btn = ctk.CTkButton(
            btn_row1,
            text="📁 输出目录",
            height=38,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            fg_color=("#e9ecef", "#2a2a4a"),
            text_color=theme.text(),
            hover_color=("#dee2e6", "#3a3a5a"),
            corner_radius=8,
            command=on_select_output_dir,
        )
        self.output_btn._is_outline = True
        self.output_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.process_btn = ctk.CTkButton(
            btn_row1,
            text="▶ 解码",
            height=38,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            fg_color="#0d6efd",
            hover_color="#0b5ed7",
            corner_radius=8,
            command=on_decode,
        )
        self.process_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        btn_row2 = ctk.CTkFrame(actions_card, fg_color="transparent")
        btn_row2.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.replace_btn = ctk.CTkButton(
            btn_row2,
            text="🔍 替换",
            height=38,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            fg_color="#6f42c1",
            hover_color="#5a32a3",
            corner_radius=8,
            command=on_replace,
        )
        self.replace_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.reencode_btn = ctk.CTkButton(
            btn_row2,
            text="🔒 编码",
            height=38,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            fg_color="#fd7e14",
            hover_color="#e3620a",
            corner_radius=8,
            command=on_reencode,
        )
        self.reencode_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))

        self.save_btn = ctk.CTkButton(
            btn_row2,
            text="💾 保存",
            height=38,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            fg_color="#198754",
            hover_color="#157347",
            corner_radius=8,
            state=tk.DISABLED,
            command=on_save,
        )
        self.save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

    def get_search_text(self) -> str:
        return self.search_entry.get()

    def get_replace_text(self) -> str:
        return self.replace_entry.get()

    def is_regex(self) -> bool:
        return self.is_regex_var.get()

    def get_output_dir(self) -> str:
        return self.output_path.get()

    def set_output_dir(self, path: str):
        self.output_path.set(path)

    def disable_buttons(self, reencode_only=False):
        self.process_btn.configure(state=tk.DISABLED)
        self.replace_btn.configure(state=tk.DISABLED)
        self.reencode_btn.configure(state=tk.DISABLED)
        if not reencode_only:
            self.save_btn.configure(state=tk.DISABLED)

    def enable_buttons(self, reencode_only=False):
        self.process_btn.configure(state=tk.NORMAL)
        self.replace_btn.configure(state=tk.NORMAL)
        self.reencode_btn.configure(state=tk.NORMAL)
        if not reencode_only:
            self.save_btn.configure(state=tk.NORMAL)

    def enable_save_button(self):
        self.save_btn.configure(state=tk.NORMAL)

    def disable_save_button(self):
        self.save_btn.configure(state=tk.DISABLED)

    def refresh_theme(self, theme: ThemeManager):
        pass
