"""Message Capable Interface , with custom metadata classes"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from playwright.async_api import Page

from src.Interfaces.Message_Interface import message_interface


class MediaType(str, Enum):
    """Constant Type set"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"


@dataclass(frozen=True)
class FileTyped:
    """Custom File  type for sending"""
    uri: str  # local path or URL
    name: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None


class MediaCapableInterface(ABC):
    @abstractmethod
    def __init__(self, page : Page):
        pass

    @abstractmethod
    async def media_add(self, mtype: MediaType, Message: message_interface, file: FileTyped) -> bool:
        """
        Attach Media given with the Type to attach to the message.
        Returns True if the media was successfully added else False.
        """
        pass
