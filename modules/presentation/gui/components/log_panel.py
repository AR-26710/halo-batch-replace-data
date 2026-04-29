from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from modules.presentation.gui.theme import ThemeManager

LOG_TAG_COLORS = {
    "info": ("#1a1a2e", "#e0e0e0"),
    "warning": ("#856404", "#ffc107"),
    "error": ("#dc3545", "#ff6b6b"),
    "success": ("#198754", "#75d9a3"),
}


class LogPanelFrame(ctk.CTkFrame):
    def __init__(self, master, theme: ThemeManager, **kwargs):
        super().__init__(master, fg_color=theme.card(), corner_radius=12, **kwargs)
        self._card_type = True
        self.pack(fill=ctk.X, padx=20, pady=(12, 20))

        self._theme = theme
        self._expanded = False

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill=tk.X, padx=20, pady=(14, 8))

        self.log_title = ctk.CTkLabel(
            header,
            text="处理日志",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=theme.text(),
        )
        self.log_title.pack(side=tk.LEFT)

        btn_group = ctk.CTkFrame(header, fg_color="transparent")
        btn_group.pack(side=tk.RIGHT)

        self.clear_btn = ctk.CTkButton(
            btn_group,
            text="清空",
            width=60,
            height=28,
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            fg_color="transparent",
            border_width=1,
            border_color=theme.border(),
            text_color=theme.text(),
            hover_color=theme.border(),
            corner_radius=6,
            command=self.clear,
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.copy_btn = ctk.CTkButton(
            btn_group,
            text="复制",
            width=60,
            height=28,
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            fg_color="transparent",
            border_width=1,
            border_color=theme.border(),
            text_color=theme.text(),
            hover_color=theme.border(),
            corner_radius=6,
            command=self.copy,
        )
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.toggle_btn = ctk.CTkButton(
            btn_group,
            text="展开",
            width=60,
            height=28,
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            fg_color="transparent",
            border_width=1,
            border_color=theme.border(),
            text_color=theme.text(),
            hover_color=theme.border(),
            corner_radius=6,
            command=self._toggle,
        )
        self.toggle_btn.pack(side=tk.LEFT)

        self.log_text = ctk.CTkTextbox(
            self,
            height=200,
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8,
            state=tk.DISABLED,
            wrap=tk.WORD,
            fg_color=theme.bg(),
            text_color=theme.text(),
            border_color=theme.border(),
        )

        self._configure_log_tags()

    def _configure_log_tags(self):
        mode = ctk.get_appearance_mode()
        for level, (light_color, dark_color) in LOG_TAG_COLORS.items():
            color = light_color if mode == "Light" else dark_color
            self.log_text.tag_config(f"log_{level}", foreground=color)

    def _toggle(self):
        self._expanded = not self._expanded
        if self._expanded:
            self.log_text.pack(fill=ctk.X, padx=16, pady=(0, 16))
            self.toggle_btn.configure(text="收起")
        else:
            self.log_text.pack_forget()
            self.toggle_btn.configure(text="展开")

    def log_message(self, message: str, level: str = "info"):
        self.log_text.configure(state=tk.NORMAL)
        start_idx = self.log_text.index(tk.END)
        self.log_text.insert(tk.END, message + "\n")
        end_idx = self.log_text.index(f"{start_idx} lineend")
        self.log_text.tag_add(f"log_{level}", start_idx, end_idx)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def clear(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def copy(self):
        root = self.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(self.log_text.get("1.0", tk.END))

    def refresh_theme(self, theme: ThemeManager):
        self._theme = theme
        self._configure_log_tags()
