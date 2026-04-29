from __future__ import annotations

import customtkinter as ctk

from modules.presentation.gui.theme import ThemeManager


class HeaderFrame(ctk.CTkFrame):
    def __init__(self, master, theme: ThemeManager, on_toggle_appearance, **kwargs):
        super().__init__(master, fg_color=theme.card(), height=56, corner_radius=0, **kwargs)
        self.pack(fill=ctk.X, padx=0, pady=0)
        self.pack_propagate(False)

        self._theme = theme
        self._on_toggle_appearance = on_toggle_appearance

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill=ctk.BOTH, expand=True, padx=24, pady=8)

        self._title_label = ctk.CTkLabel(
            inner,
            text="Halo 数据批量替换器",
            font=ctk.CTkFont(family="Microsoft YaHei", size=20, weight="bold"),
            text_color=theme.text(),
        )
        self._title_label.pack(side=ctk.LEFT)

        self._appearance_btn = ctk.CTkButton(
            inner,
            text="🌙 深色模式",
            width=110,
            height=34,
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            fg_color="transparent",
            border_width=1,
            border_color=theme.border(),
            text_color=theme.text(),
            hover_color=theme.border(),
            command=self._handle_toggle,
        )
        self._appearance_btn._is_outline = True
        self._appearance_btn.pack(side=ctk.RIGHT)

    def _handle_toggle(self):
        self._on_toggle_appearance()
        current = ctk.get_appearance_mode()
        if current == "Dark":
            self._appearance_btn.configure(text="☀️ 浅色模式")
        else:
            self._appearance_btn.configure(text="🌙 深色模式")

    def refresh_theme(self, theme: ThemeManager):
        pass
