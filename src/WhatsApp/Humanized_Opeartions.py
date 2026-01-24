"""All Humanized Operation Classes"""
from __future__ import annotations

from playwright.async_api import Page

from src.Interfaces.Humanize_Operation_Interface import humanize_operation


class Humanized_Operation(humanize_operation):
    """WhatsApp  Customized Humanized Operation"""

    def __init__(self, page: Page):
        super().__init__(page=page)

    async def operation_typing(self, text: str) -> None:
        pass
