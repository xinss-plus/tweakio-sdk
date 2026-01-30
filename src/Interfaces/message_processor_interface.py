"""Message Processor Interface Must be implemented by every Message Processor implementation."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from playwright.async_api import Page

from src.Interfaces.chatinterface import ChatInterface
from src.MessageFilter import Filter
from messageinterface import MessageInterface
from sql_lite_storage import SQL_Lite_Storage
from src.WhatsApp.WebUISelector import WebSelectorConfig


class MessageProcessorInterface(ABC):
    """
    Message Processor Interface for Messages
    """

    def __init__(
            self,
            log : logging.Logger,
            page : Page,
            UIConfig: WebSelectorConfig,
            storage_obj: Optional[SQL_Lite_Storage] = None,
            filter_obj: Optional[Filter] = None
    ) -> None:
        self.storage = storage_obj
        self.filter = filter_obj
        self.log = log
        self.page = page
        self.UIConfig = UIConfig

    @abstractmethod
    async def _get_wrapped_Messages(self, retry: int, *args, **kwargs) -> List[MessageInterface]: pass

    @abstractmethod
    async def Fetcher(self, chat: ChatInterface, retry: int, *args, **kwargs) -> List[MessageInterface]:
        """
        Returns the List of Total messages in that open Chat/Contact.
        Flexibility with batch processing & Safer Filtering approaches.
        """
        pass
