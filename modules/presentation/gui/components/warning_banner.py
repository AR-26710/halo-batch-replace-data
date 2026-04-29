from __future__ import annotations

import customtkinter as ctk

from modules.presentation.gui.theme import ThemeManager


class WarningBannerFrame(ctk.CTkFrame):
    def __init__(self, master, theme: ThemeManager, **kwargs):
        super().__init__(master, fg_color=("#fff3cd", "#3d3400"), height=40, corner_radius=8, **kwargs)
        self.pack(fill=ctk.X, padx=20, pady=(12, 0))
        self.pack_propagate(False)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill=ctk.BOTH, expand=True, padx=16, pady=6)

        warn_label = ctk.CTkLabel(
            inner,
            text="⚠️  不保证数据稳定！请做好完整的数据备份！",
            font=ctk.CTkFont(family="Microsoft YaHei", size=13, weight="bold"),
            text_color=("#856404", "#ffc107"),
        )
        warn_label._is_warning_text = True
        warn_label.pack()

    def refresh_theme(self, theme: ThemeManager):
        self.configure(fg_color=("#fff3cd", "#3d3400"))
