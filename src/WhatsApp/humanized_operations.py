"""All Humanized Operation Classes"""
from __future__ import annotations

import logging
import random
from typing import Union, Optional

import pyperclip
from playwright.async_api import Page, ElementHandle, Locator

from src.Interfaces.humanize_operation_interface import HumanizeOperation
from src.Interfaces.web_ui_selector import WebUISelectorCapable


class HumanizedOperations(HumanizeOperation):
    """WhatsApp  Customized Humanized Operation"""

    def __init__(self, page: Page, log: logging.Logger, UIConfig : WebUISelectorCapable):
        super().__init__(page=page, log=log, UIConfig=UIConfig)

    async def typing(self, text: str, **kwargs) -> bool:
        source: Optional[Union[ElementHandle, Locator]] = kwargs.get("source") or None
        if not source:
            raise Exception("Wrong Method Assigned , need clickable_source in wa/ humanize / typing")

        try:

            await source.click(timeout=3000)  # 3 sec for Humanized Typing handling by camoufox

            # Clear previous text
            await source.press("Control+A")
            await source.press("Backspace")

            # Todo , grabbing the real clipboard context , by pyperclip for better debugging
            self.log.info("Cleared Previous text in input box")

            lines = text.split("\n")

            if len(text) <= 50:
                await self.page.keyboard.type(text=text, delay=random.randint(80, 100))
            else:
                for i, line in enumerate(lines):

                    # if more than 50 char limit , use clipboard and paste it.
                    if len(line) > 50:
                        pyperclip.copy(line)
                        await self.page.keyboard.press("Control+V")
                    else:  # Else Type with random typing speed
                        await self.page.keyboard.type(text=line, delay=random.randint(80, 100))

                    # if /n comes , write it to another line,
                    if i < len(lines) - 1:
                        await self.page.keyboard.press("Shift+Enter")
            return True
        except Exception as e:
            self.log.warning(f" WA / Humanized_Operation / typing , Failed Typing : {e}", exc_info=True)
            return await self._Instant_fill(text=text, source=source)

    async def _Instant_fill(self, text: str, source: Optional[Union[ElementHandle, Locator]]) -> bool:
        if not source :
            raise Exception("WA / Humanized_Operation / __instant_fill, need clickable_source")
        try:
            await source.fill(text)
            await self.page.keyboard.press("Enter")
            return True
        except Exception as e:
            self.log.error(f" WA / Humanized_Operation / typing , Failed the direct fill .: {e}", exc_info=True)
            await self.page.keyboard.press("Escape", delay=0.5)
            await self.page.keyboard.press("Escape", delay=0.5)
        return False
