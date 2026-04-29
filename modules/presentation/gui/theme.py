from __future__ import annotations

import customtkinter as ctk


class ThemeManager:
    def __init__(self):
        self._listeners: list = []

    def add_listener(self, listener):
        self._listeners.append(listener)

    def get_bg_color(self) -> str:
        mode = ctk.get_appearance_mode()
        return "#1a1a2e" if mode == "Dark" else "#f0f2f5"

    def get_card_color(self) -> str:
        mode = ctk.get_appearance_mode()
        return "#16213e" if mode == "Dark" else "#ffffff"

    def get_text_color(self) -> str:
        mode = ctk.get_appearance_mode()
        return "#e0e0e0" if mode == "Dark" else "#1a1a2e"

    def get_sub_text_color(self) -> str:
        mode = ctk.get_appearance_mode()
        return "#a0a0b0" if mode == "Dark" else "#6c757d"

    def get_border_color(self) -> str:
        mode = ctk.get_appearance_mode()
        return "#2a2a4a" if mode == "Dark" else "#e0e0e0"

    def bg(self) -> tuple[str, str]:
        return ("#f0f2f5", "#1a1a2e")

    def card(self) -> tuple[str, str]:
        return ("#ffffff", "#16213e")

    def text(self) -> tuple[str, str]:
        return ("#1a1a2e", "#e0e0e0")

    def sub_text(self) -> tuple[str, str]:
        return ("#6c757d", "#a0a0b0")

    def border(self) -> tuple[str, str]:
        return ("#e0e0e0", "#2a2a4a")

    def toggle_appearance(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def refresh_all(self):
        for listener in self._listeners:
            listener.refresh_theme(self)
