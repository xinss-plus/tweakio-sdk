"""
This is an ChatInterFace to implement and usage
for every Platform Chat Based Objects.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from playwright.async_api import ElementHandle


class chat_interface(ABC):
    """Interface for Chat for every Platform """

    chatName: Optional[str]
    chatID: Optional[str]
    ChatUI: Optional[Union[ElementHandle, Locator]]
    System_Hit_Time: float

    @abstractmethod
    def _chat_key(self, **kwargs) -> str:
        """Returns the Hashed UI"""
        pass
