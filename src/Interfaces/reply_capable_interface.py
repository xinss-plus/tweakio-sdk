"""Every Reply must implement a ReplyCapable interface"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from playwright.async_api import Page

from src.Interfaces.Humanize_Operation_Interface import humanize_operation
from src.Interfaces.Message_Interface import message_interface


class ReplyCapableInterface(ABC):
    """AAbstract class to represent ReplyCapable interface"""

    def __init__(self, page: Page, log: logging.Logger, **kwargs) -> None:
        self.page = page
        self.log = log

    @abstractmethod
    async def reply(self, Message: message_interface, humanize: humanize_operation, text: Optional[str], **kwargs) -> bool:
        """Reply  to the message and returns True on success else False"""
        pass
