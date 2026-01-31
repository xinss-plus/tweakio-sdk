"""WhatsApp Customized Reply Module"""

from __future__ import annotations

import logging
import random
from typing import Optional

from playwright.async_api import Page, Locator, Position
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from humanized_operations import HumanizedOperations
from src.Exceptions.base import ReplyCapableError
from src.Interfaces.reply_capable_interface import ReplyCapableInterface
from src.Interfaces.web_ui_selector import WebUISelectorCapable
from src.WhatsApp.DerivedTypes.Message import whatsapp_message


class ReplyCapable(ReplyCapableInterface):
    def __init__(self, page: Page, log: logging.Logger, UIConfig: WebUISelectorCapable):
        super().__init__(page=page, log=log, UIConfig=UIConfig)
        if self.page is None:
            raise ValueError("page must not be None")

    async def reply(
            self,
            message: whatsapp_message,
            humanize: HumanizedOperations,
            text: Optional[str],
            **kwargs
    ) -> bool:
        """
        reply to the message.
        params :
            text : text to add while replying.
            humanize : humanize_operation module or custom module to type humanized
            message : target element

        return True on success, False otherwise

        raises :
            Timeout error with ReplyCapableError wrapped
        """
        try:
            await self._side_edge_click(message)

            in_box = self.UIConfig.message_box(self.page)
            await in_box.click(timeout=3000)

            text = text or ""
            success = await humanize.typing(
                source=await in_box.element_handle(timeout=1000),
                text=text
            )

            if success:
                await self.page.keyboard.press("Enter")

            return success

        except PlaywrightTimeoutError as e:
            raise ReplyCapableError(
                "reply timed out while preparing input box"
            ) from e

    async def _side_edge_click(self, message: whatsapp_message) -> bool:
        """
        Clicks edges of the message based on direction.

        returns True on success, False otherwise

        Raises
            - Timeout error as PlaywrightTimeoutError with ReplyCapableError wrapped
        """
        ui = message.MessageUI
        try:
            if isinstance(ui, Locator):
                ui = await ui.element_handle(timeout=1000)

            await ui.scroll_into_view_if_needed(timeout=2000)
            box = await ui.bounding_box()
            if not box:
                raise ReplyCapableError("message bounding box not available")

            rel_x = box["width"] * (0.2 if message.isIncoming() else 0.8)
            rel_y = box["height"] / 2

            await ui.click(
                position=Position(x=rel_x, y=rel_y),
                click_count=2,
                delay=random.randint(55, 70),
                timeout=3000
            )

            await self.page.wait_for_timeout(timeout=500)
            return True

        except PlaywrightTimeoutError as e:
            raise ReplyCapableError(
                "side_edge_click timed out while clicking message UI"
            ) from e
