"""Message Capable Interface , with custom metadata classes"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from playwright.async_api import Page

from src.Interfaces.Message_Interface import message_interface
from src.Interfaces.Web_UI_Selector import WebUISelectorCapable


class MediaType(str, Enum):
    """Constant Media Type to restrict it to same names & constraint."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


@dataclass(frozen=True)
class FileTyped:
    """Custom File  type for sending"""
    uri: str  # local path or URL
    name: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None


class MediaCapableInterface(ABC):
    """Media Capable Interface"""

    @abstractmethod
    def __init__(self, page: Page, log: logging.Logger, UIConfig: WebUISelectorCapable, **kwargs) -> None:
        self.page = page
        self.log = log
        self.UIConfig = UIConfig

    @abstractmethod
    async def add_media(self, mtype: MediaType, Message: message_interface, file: FileTyped, **kwargs) -> bool:
        """
        Attach Media given with the Type to attach to the message.
        Returns True if the media was successfully added else False.
        """
        pass
