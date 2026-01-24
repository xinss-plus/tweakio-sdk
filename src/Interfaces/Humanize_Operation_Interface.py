"""All the Humanized Operation Interface modules"""
from abc import ABC, abstractmethod

from playwright.async_api import Page


class humanize_operation(ABC):

    @abstractmethod
    def __init__(self, page: Page) -> None:
        self.page = page

    @abstractmethod
    async def operation_typing(self, text: str) -> None:
        """This operation ensures the given text is typed on the Web UI with humanized Typing"""
        pass
