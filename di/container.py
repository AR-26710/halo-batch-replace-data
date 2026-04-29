from __future__ import annotations

from modules.application.use_cases.batch_replace_use_case import BatchReplaceUseCase
from modules.application.use_cases.delete_extension_use_case import DeleteExtensionUseCase
from modules.application.use_cases.export_extensions_use_case import ExportExtensionsUseCase
from modules.application.use_cases.load_extensions_use_case import LoadExtensionsUseCase
from modules.application.use_cases.reset_extensions_use_case import ResetExtensionsUseCase
from modules.application.use_cases.update_extension_use_case import UpdateExtensionUseCase
from modules.core.di.container import DIContainer, Provider
from modules.core.events.event_bus import SimpleEventBus
from modules.core.logging.logger import ConsoleLogger
from modules.infrastructure.repositories.file_storage_repository import FileStorageRepository
from modules.infrastructure.repositories.in_memory_extension_repository import InMemoryExtensionRepository
from modules.infrastructure.services.encoding.base64_decoder import Base64Decoder
from modules.infrastructure.services.encoding.base64_encoder import Base64Encoder
from modules.infrastructure.services.replace.default_replace_engine import DefaultReplaceEngine


def configure_container() -> DIContainer:
    c = DIContainer()

    c.register(Provider(provide='IEventBus', use_value=SimpleEventBus()))
    c.register(Provider(provide='ILogger', use_value=ConsoleLogger()))

    ext_repo = InMemoryExtensionRepository()
    c.register(Provider(provide='IExtensionRepository', use_value=ext_repo))
    c.register(Provider(provide='IStorageRepository', use_value=FileStorageRepository()))
    c.register(Provider(provide='Base64Decoder', use_value=Base64Decoder()))
    c.register(Provider(provide='Base64Encoder', use_value=Base64Encoder()))
    c.register(Provider(provide='IReplaceEngine', use_value=DefaultReplaceEngine()))

    event_bus = c.resolve('IEventBus')
    extension_repo = c.resolve('IExtensionRepository')
    storage_repo = c.resolve('IStorageRepository')
    decoder = c.resolve('Base64Decoder')
    encoder = c.resolve('Base64Encoder')
    replace_engine = c.resolve('IReplaceEngine')

    c.register(Provider(provide='LoadExtensionsUseCase', use_value=LoadExtensionsUseCase(
        storage_repo, extension_repo, decoder, event_bus
    )))
    c.register(Provider(provide='ExportExtensionsUseCase', use_value=ExportExtensionsUseCase(
        extension_repo, storage_repo, encoder, event_bus
    )))
    c.register(Provider(provide='BatchReplaceUseCase', use_value=BatchReplaceUseCase(
        extension_repo, replace_engine, decoder, encoder, event_bus
    )))
    c.register(Provider(provide='ResetExtensionsUseCase', use_value=ResetExtensionsUseCase(
        extension_repo, event_bus
    )))
    c.register(Provider(provide='UpdateExtensionUseCase', use_value=UpdateExtensionUseCase(
        extension_repo, event_bus
    )))
    c.register(Provider(provide='DeleteExtensionUseCase', use_value=DeleteExtensionUseCase(
        extension_repo, event_bus
    )))

    return c


def get_use_cases(container: DIContainer) -> dict:
    return {
        'load': container.resolve('LoadExtensionsUseCase'),
        'export': container.resolve('ExportExtensionsUseCase'),
        'batch_replace': container.resolve('BatchReplaceUseCase'),
        'reset': container.resolve('ResetExtensionsUseCase'),
        'update': container.resolve('UpdateExtensionUseCase'),
        'delete': container.resolve('DeleteExtensionUseCase'),
        'extension_repo': container.resolve('IExtensionRepository'),
        'event_bus': container.resolve('IEventBus'),
    }
