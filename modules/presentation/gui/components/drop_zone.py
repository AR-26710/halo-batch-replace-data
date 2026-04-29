from __future__ import annotations

import customtkinter as ctk

from modules.presentation.gui.theme import ThemeManager


class DropZoneFrame(ctk.CTkFrame):
    def __init__(self, master, theme: ThemeManager, on_select_file, **kwargs):
        super().__init__(master, fg_color=theme.bg(), **kwargs)
        self.pack(fill=ctk.X, padx=20, pady=(12, 0))

        self._theme = theme
        self._on_select_file = on_select_file

        self._drop_card = ctk.CTkFrame(
            self,
            fg_color=theme.card(),
            corner_radius=12,
            border_width=2,
            border_color=("#c8c8c8", "#3a3a5c"),
            height=80,
        )
        self._drop_card._card_type = True
        self._drop_card.pack(fill=ctk.X, padx=0, pady=(0, 0))
        self._drop_card.pack_propagate(False)

        self._drop_inner = ctk.CTkFrame(self._drop_card, fg_color="transparent")
        self._drop_inner.pack(fill=ctk.BOTH, expand=True, padx=20, pady=8)

        self._drop_icon_label = ctk.CTkLabel(
            self._drop_inner,
            text="📂",
            font=ctk.CTkFont(size=24),
            text_color=theme.sub_text(),
        )
        self._drop_icon_label._is_sub_text = True
        self._drop_icon_label.pack(pady=(0, 2))

        self._drop_label = ctk.CTkLabel(
            self._drop_inner,
            text="拖拽文件到此处 或 点击选择文件",
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            text_color=theme.sub_text(),
            justify=ctk.CENTER,
        )
        self._drop_label._is_sub_text = True
        self._drop_label.pack()

        for widget in [self._drop_card, self._drop_inner, self._drop_icon_label, self._drop_label]:
            widget.bind("<Button-1>", lambda e: self._on_select_file())
            widget.bind("<Enter>", lambda e: self._on_drop_hover(True))
            widget.bind("<Leave>", lambda e: self._on_drop_hover(False))

    def _on_drop_hover(self, entering):
        if entering:
            self._drop_label.configure(text_color=("#1f6aa5", "#5dade2"))
        else:
            self._drop_label.configure(text_color=self._theme.sub_text())

    def update_message(self, message: str):
        self._drop_label.configure(text=message, text_color=("#198754", "#75d9a3"))

    def reset_message(self):
        self._drop_label.configure(
            text="拖拽文件到此处\n或点击此处选择文件",
            text_color=self._theme.sub_text(),
        )

    def refresh_theme(self, theme: ThemeManager):
        pass
