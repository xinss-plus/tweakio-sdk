"""WhatsApp Customized Reply Module"""

from __future__ import annotations

import logging
import random

from typing import Optional
from playwright.async_api import Page, Locator, Position

from Humanized_Opeartions import Humanized_Operation
from src.Interfaces.Reply_Capabale_Interface import ReplyCapableInterface
from src.WhatsApp.DefinedClasses.Message import whatsapp_message
import WebUISelector as sc
class Reply(ReplyCapableInterface):
    def __init__(self, page: Page, log : logging.Logger):
        super().__init__(page=page, log=log)

# Todo, In future Version Media Module will be added in the Reply to give the reference
    async def reply(self, Message: whatsapp_message, humanize: Humanized_Operation, text : Optional[str]) -> bool:
        try :
            side_click_success = await self.side_edge_click(Message=Message)

            # Todo , Add with Logger Refined Function
            if not side_click_success:
                raise Exception("WA")

            # send the text as humanized safely
            in_box = sc.message_box(self.page)
            await in_box.click(timeout=3000)
            if not text: text = ""
            check_success = await humanize.typing(source=await in_box.element_handle(timeout=1000), text=text)

            if check_success  :
                await self.page.keyboard.press("Enter")
            return check_success
        except Exception as e:
            self.log.warning(f" WA / reply / Error : {e}", exc_info=True)
            return False


    async def side_edge_click(self, Message: whatsapp_message) -> bool:
        """Clicks the message on the side based on incoming & outgoing"""
        try:
            # TypeCase it to the ElementHandle
            if isinstance(Message.MessageUI, Locator):
                Message.MessageUI = await Message.MessageUI.element_handle(timeout=1000)

            await Message.MessageUI.scroll_into_view_if_needed(timeout=2000)
            box = await Message.MessageUI.bounding_box()

            if not box : return False

            rel_x = box["width"] * (0.2 if Message.isIncoming() else 0.8)
            rel_y = box["height"] / 2

            await Message.MessageUI.click(
                position= Position(x=rel_x, y=rel_y),
                click_count=2,
                delay=random.randint(55 , 70),
                timeout=3000
            )

            # Delay for UI reaction
            await self.page.wait_for_timeout(timeout=500)
            return True

        except Exception as e:
            self.log.error(f" WA / side_edge_click / Error : {e}", exc_info=True)
            return False
