from modules.infrastructure.types import (
    ReplaceRule, ReplaceScope, PreviewChange, ReplaceResult,
    BatchReplaceResult, IReplaceEngine
)
from modules.infrastructure.repositories import InMemoryExtensionRepository, FileStorageRepository, FileFormatError
from modules.infrastructure.services.encoding import Base64Decoder, base64_decoder, Base64Encoder, base64_encoder
from modules.infrastructure.services.replace import DefaultReplaceEngine, default_replace_engine
