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
from src.WhatsApp.DefinedClasses.Message import whatsapp_message


class ReplyHandle(ReplyCapableInterface):
    def __init__(self, page: Page, log: logging.Logger, UIConfig: WebUISelectorCapable):
        super().__init__(page=page, log=log, UIConfig=UIConfig)

    # Todo, In future Version Media Module will be added in the Reply to give the reference
    async def reply(self, Message: whatsapp_message, humanize: HumanizedOperations, text: Optional[str],
                    **kwargs) -> bool:
        await self.side_edge_click(Message)

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

    async def side_edge_click(self, Message: whatsapp_message) -> bool:
        """Clicks the message on the side based on incoming & outgoing"""

        try:
            if isinstance(Message.MessageUI, Locator):
                Message.MessageUI = await Message.MessageUI.element_handle(timeout=1000)

            await Message.MessageUI.scroll_into_view_if_needed(timeout=2000)
            box = await Message.MessageUI.bounding_box()
            if not box:
                return False

            rel_x = box["width"] * (0.2 if Message.isIncoming() else 0.8)
            rel_y = box["height"] / 2

            await Message.MessageUI.click(
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
