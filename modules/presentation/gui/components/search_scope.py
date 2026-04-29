from __future__ import annotations

import sys

import tkinter as tk

import customtkinter as ctk

from modules.infrastructure.types.replace_types import ReplaceScope
from modules.presentation.gui.theme import ThemeManager


SCOPE_FIELDS = [
    ("search_in_name", "扩展名称 (name)"),
    ("search_in_kind", "类型 (kind)"),
    ("search_in_metadata_name", "元数据名称 (metadata.name)"),
    ("search_in_api_version", "API 版本 (apiVersion)"),
    ("search_in_data", "数据字段 (data)"),
    ("search_in_spec", "规格字段 (spec)"),
]


class SearchScopeFrame(ctk.CTkFrame):
    def __init__(self, master, theme: ThemeManager, **kwargs):
        super().__init__(master, fg_color=theme.bg(), **kwargs)
        self.pack(fill=ctk.X, padx=20, pady=(12, 0))

        self._theme = theme
        self._scope_vars: dict[str, tk.BooleanVar] = {}
        self._selected_kinds: list[str] = []
        self._kind_vars: dict[str, tk.BooleanVar] = {}
        self._kinds_frame: ctk.CTkFrame | None = None
        self._kinds_container: ctk.CTkFrame | None = None

        self._build_card(theme)

    def _build_card(self, theme: ThemeManager):
        self._card = ctk.CTkFrame(self, fg_color=theme.card(), corner_radius=12)
        self._card._card_type = True
        self._card.pack(fill=ctk.X)

        header_frame = ctk.CTkFrame(self._card, fg_color="transparent")
        header_frame.pack(fill=tk.X, padx=20, pady=(16, 4))

        ctk.CTkLabel(
            header_frame,
            text="🔍 搜索范围",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=theme.text(),
        ).pack(side=tk.LEFT)

        self._toggle_btn = ctk.CTkButton(
            header_frame,
            text="收起 ▲",
            width=60,
            height=28,
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            fg_color="transparent",
            text_color=theme.sub_text(),
            hover_color=theme.border(),
            corner_radius=6,
            command=self._toggle_collapse,
        )
        self._toggle_btn.pack(side=tk.RIGHT)

        self._content_frame = ctk.CTkFrame(self._card, fg_color="transparent")
        self._content_frame.pack(fill=tk.X, padx=20, pady=(0, 16))

        self._build_scope_section(theme)
        self._build_kind_section(theme)

        self._is_collapsed = False

    def _build_scope_section(self, theme: ThemeManager):
        scope_label = ctk.CTkLabel(
            self._content_frame,
            text="搜索范围",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12, weight="bold"),
            text_color=theme.text(),
        )
        scope_label.pack(anchor=tk.W, pady=(8, 6))

        grid_frame = ctk.CTkFrame(self._content_frame, fg_color="transparent")
        grid_frame.pack(fill=tk.X)

        for i, (field_key, label_text) in enumerate(SCOPE_FIELDS):
            row = i // 2
            col = i % 2

            cell_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
            cell_frame.grid(row=row, column=col, sticky=tk.W, padx=(0, 16), pady=2)

            var = tk.BooleanVar(value=True)
            self._scope_vars[field_key] = var

            checkbox = ctk.CTkCheckBox(
                cell_frame,
                text=label_text,
                variable=var,
                font=ctk.CTkFont(family="Microsoft YaHei", size=12),
                text_color=theme.text(),
                checkbox_width=20,
                checkbox_height=20,
                corner_radius=4,
            )
            checkbox.pack(anchor=tk.W)

        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

    def _build_kind_section(self, theme: ThemeManager):
        self._kind_separator = ctk.CTkFrame(self._content_frame, height=1, fg_color=theme.border())

        self._kind_header = ctk.CTkFrame(self._content_frame, fg_color="transparent")

        ctk.CTkLabel(
            self._kind_header,
            text="类型筛选",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12, weight="bold"),
            text_color=theme.text(),
        ).pack(side=tk.LEFT)

        ctk.CTkLabel(
            self._kind_header,
            text="（不选择任何类型将替换所有类型）",
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            text_color=theme.sub_text(),
        ).pack(side=tk.LEFT, padx=(8, 0))

        self._kinds_container = ctk.CTkScrollableFrame(
            self._content_frame,
            fg_color=theme.card(),
            height=120,
            corner_radius=0,
            scrollbar_button_color=theme.border(),
            scrollbar_button_hover_color=theme.sub_text(),
        )

        self._no_kinds_label = ctk.CTkLabel(
            self._kinds_container,
            text="请先加载文件以获取可用类型",
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            text_color=theme.sub_text(),
        )
        self._no_kinds_label._is_sub_text = True
        self._no_kinds_label.pack(anchor=tk.W, pady=(4, 0))

        self._kinds_frame = ctk.CTkFrame(self._kinds_container, fg_color="transparent")

        self._setup_scroll_guard()

    def _setup_scroll_guard(self):
        root = self.winfo_toplevel()
        container_frame = self._kinds_container._parent_frame

        def _is_mouse_in_container(event):
            if not container_frame.winfo_viewable():
                return False
            x = container_frame.winfo_rootx()
            y = container_frame.winfo_rooty()
            return (x <= event.x_root <= x + container_frame.winfo_width() and
                    y <= event.y_root <= y + container_frame.winfo_height())

        def _on_mousewheel(event):
            if not _is_mouse_in_container(event):
                return
            canvas = self._kinds_container._parent_canvas
            if canvas.yview() == (0.0, 1.0):
                return
            if sys.platform.startswith("win"):
                canvas.yview("scroll", -int(event.delta / 6), "units")
            else:
                canvas.yview("scroll", -event.delta, "units")
            return "break"

        def _on_mousewheel_linux(event):
            if not _is_mouse_in_container(event):
                return
            canvas = self._kinds_container._parent_canvas
            if canvas.yview() == (0.0, 1.0):
                return
            if event.num == 4:
                canvas.yview("scroll", -1, "units")
            elif event.num == 5:
                canvas.yview("scroll", 1, "units")
            return "break"

        root.bind("<MouseWheel>", _on_mousewheel, add="+")
        root.bind("<Button-4>", _on_mousewheel_linux, add="+")
        root.bind("<Button-5>", _on_mousewheel_linux, add="+")

    def _toggle_collapse(self):
        if self._is_collapsed:
            self._content_frame.pack(fill=tk.X, padx=20, pady=(0, 16))
            self._toggle_btn.configure(text="收起 ▲")
        else:
            self._content_frame.pack_forget()
            self._toggle_btn.configure(text="展开 ▼")
        self._is_collapsed = not self._is_collapsed

    def _show_kind_section(self):
        self._kind_separator.pack(fill=tk.X, pady=(12, 0))
        self._kind_header.pack(fill=tk.X, pady=(8, 2))
        self._kinds_container.pack(fill=tk.X)

    def _hide_kind_section(self):
        self._kind_separator.pack_forget()
        self._kind_header.pack_forget()
        self._kinds_container.pack_forget()

    def update_kinds(self, kinds: list[str]):
        if self._kinds_frame:
            for child in self._kinds_frame.winfo_children():
                child.destroy()
        self._kind_vars.clear()

        if not kinds:
            self._hide_kind_section()
            return

        self._no_kinds_label.pack_forget()
        self._show_kind_section()

        kinds_grid = ctk.CTkFrame(self._kinds_frame, fg_color="transparent")
        kinds_grid.pack(fill=tk.X, pady=(4, 0))

        for i, kind in enumerate(kinds):
            row = i // 3
            col = i % 3

            cell_frame = ctk.CTkFrame(kinds_grid, fg_color="transparent")
            cell_frame.grid(row=row, column=col, sticky=tk.W, padx=(0, 12), pady=2)

            var = tk.BooleanVar(value=False)
            self._kind_vars[kind] = var

            checkbox = ctk.CTkCheckBox(
                cell_frame,
                text=kind,
                variable=var,
                font=ctk.CTkFont(family="Microsoft YaHei", size=11),
                text_color=self._theme.text(),
                checkbox_width=18,
                checkbox_height=18,
                corner_radius=4,
            )
            checkbox.pack(anchor=tk.W)

        for c in range(3):
            kinds_grid.columnconfigure(c, weight=1)

        self._kinds_frame.pack(fill=tk.X)

    def get_scope(self) -> ReplaceScope:
        selected_kinds = [kind for kind, var in self._kind_vars.items() if var.get()]

        return ReplaceScope(
            search_in_name=self._scope_vars["search_in_name"].get(),
            search_in_kind=self._scope_vars["search_in_kind"].get(),
            search_in_metadata_name=self._scope_vars["search_in_metadata_name"].get(),
            search_in_api_version=self._scope_vars["search_in_api_version"].get(),
            search_in_data=self._scope_vars["search_in_data"].get(),
            search_in_spec=self._scope_vars["search_in_spec"].get(),
            selected_kinds=selected_kinds,
        )

    def reset_scope(self):
        for var in self._scope_vars.values():
            var.set(True)
        for var in self._kind_vars.values():
            var.set(False)

    def refresh_theme(self, theme: ThemeManager):
        pass
