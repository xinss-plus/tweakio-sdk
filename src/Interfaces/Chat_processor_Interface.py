"""
This is a Chat Loading Interface contract .
It will help give the Basic Functions like fetching and giving list of Chat Objs.
Ex : Fetch , wrappedChats , ChatClicker

Any Specific Function will be defined via Child Class as if those are platform Independent.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from playwright.async_api import Page

from src.Interfaces.Chat_Interface import chat_interface
from src.WhatsApp.WebUISelector import WebSelectorConfig


class chat_processor_interface(ABC):
    """Chat Loader Interface"""
    capabilities: Dict[str, bool]

    def __init__(self, log: logging.Logger, page : Page, UIConfig : WebSelectorConfig, **kwargs) -> None:
        self.log = log
        self.page = page
        self.UIConfig = UIConfig

    @abstractmethod
    async def fetch_chats(self, **kwargs) -> List[chat_interface]:
        """Fetch and return limited chat objects"""
        pass

    @abstractmethod
    async def _click_chat(self, chat: Optional[chat_interface], **kwargs) -> bool:
        """Click chat object"""
        pass

    @abstractmethod
    async def _get_Wrapped_Chat(self, *args, **kwargs) -> List[chat_interface]: pass
