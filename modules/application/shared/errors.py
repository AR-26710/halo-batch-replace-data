from __future__ import annotations

class ExtensionNotFoundError(Exception):
    def __init__(self, name: str):
        super().__init__(f'Extension not found: {name}')
        self.name = name


class NoExtensionsError(Exception):
    def __init__(self):
        super().__init__('No extensions to export')


class FileFormatError(Exception):
    def __init__(self, message: str, code: str = 'UNKNOWN'):
        super().__init__(message)
        self.code = code
