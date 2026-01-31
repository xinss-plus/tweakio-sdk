"""Every Reply must implement a ReplyCapable interface"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from playwright.async_api import Page

from src.Interfaces.humanize_operation_interface import HumanizeOperation
from src.Interfaces.message_interface import MessageInterface
from src.Interfaces.web_ui_selector import WebUISelectorCapable


class ReplyCapableInterface(ABC):
    """AAbstract class to represent ReplyCapable interface"""

    def __init__(self, page: Page, log: logging.Logger, UIConfig: WebUISelectorCapable, **kwargs) -> None:
        self.page = page
        self.log = log
        self.UIConfig = UIConfig

    @abstractmethod
    async def reply(
            self,
            Message: MessageInterface,
            humanize: HumanizeOperation,
            text: Optional[str],
            **kwargs
    ) -> bool: ...
