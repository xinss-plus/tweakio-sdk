"""Message Interface Protocol, Every Message Class have to Implement this interface"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union

from ChatInterface import ChatInterface
from playwright.async_api import ElementHandle, Locator


class message_interface(ABC):
    """Message Interface"""

    System_Hit_Time: float
    raw_Data: str
    data_type: str
    parent_chat: ChatInterface
    MessageUI: Optional[Union[ElementHandle, Locator]]
    MessageID: Optional[str]

    @abstractmethod
    def _message_key(self, **kwargs) -> str:
        """Returns the Hashed UI"""
        pass
