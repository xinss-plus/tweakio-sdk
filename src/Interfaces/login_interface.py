import logging
from abc import ABC, abstractmethod

from playwright.async_api import Page

from src.Interfaces.web_ui_selector import WebUISelectorCapable


class LoginInterface(ABC):
    """All Must Implementable functions Interface"""

    def __init__(self, page: Page, UIConfig: WebUISelectorCapable, log: logging.Logger) -> None:
        self.page = page
        self.UIConfig = UIConfig
        self.log = log

    @abstractmethod
    async def login(self, **kwargs) -> bool: ...

    async def logout(self, **kwargs) -> bool: ...

    async def is_login_successful(self, **kwargs) -> bool: ...
