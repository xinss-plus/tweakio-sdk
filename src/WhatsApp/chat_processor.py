"""
WhatsApp based Chat Loader
"""
from __future__ import annotations

import logging
import random
from typing import Dict, List, Optional

from playwright.async_api import Page, ElementHandle, Locator
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from src.Exceptions import ChatNotFoundError, ChatClickError, TweakioError
from src.Exceptions.whatsapp import ChatProcessorError, ChatUnreadError, ChatMenuError, ChatError
from src.Interfaces.chat_processor_interface import ChatProcessorInterface
from src.WhatsApp.DerivedTypes.Chat import whatsapp_chat
from src.WhatsApp.web_ui_config import WebSelectorConfig


# Todo , add the paths for chatLoaderInterface , ChatInterface
class ChatProcessor(ChatProcessorInterface):
    """WhatsApp's Custom Chat processor """

    # Todo About the capabilities adding dynamically via functions and other Loaders providing comparison

    def __init__(self, page: Page, log: logging.Logger, UIConfig: WebSelectorConfig) -> None:
        super().__init__(page=page, log=log, UIConfig=UIConfig)
        self.capabilities: Dict[str, bool] = {}
        if self.page is None:
            raise ValueError("page must not be None")

    async def fetch_chats(self, limit: int = 5, retry: int = 5) -> List[whatsapp_chat]:
        """Fetching chats in the loaded JS UI of web page of WhatsApp"""
        ChatList: List[whatsapp_chat] = await self._get_Wrapped_Chat(limit=limit, retry=retry)

        if not ChatList:
            raise ChatNotFoundError("Chats Not Found on the Page.")

        return ChatList

    async def _get_Wrapped_Chat(self, limit: int, retry: int) -> List[whatsapp_chat]:
        """List Based Raw data of chats"""
        sc = self.UIConfig
        wrapped: List[whatsapp_chat] = []
        try:
            chats = sc.chat_items()  # return Locator of chats.
            counter = 0
            while not (await chats.count()) and counter < retry:
                chats = sc.chat_items()
                await  self.page.wait_for_timeout(1000)
                counter += 1

            count = await chats.count()
            if not count: raise ChatNotFoundError("Chats Not Found.")

            minimum = min(count, limit)
            for i in range(minimum):
                wrapperChat = whatsapp_chat(
                    chatUI=chats.nth(i),
                    chatName=await sc.getChatName(chats.nth(i))
                )
                wrapped.append(wrapperChat)

            return wrapped
        except TweakioError as e:
            raise ChatProcessorError("Failed to extract chat") from e

    # -------------------------------------------

    async def _click_chat(self, chat: Optional[whatsapp_chat], **kwargs) -> bool:
        """Chat Clicker to open."""
        try:
            if not chat:
                raise ChatNotFoundError("none passed , expected chat in click chat")

            handle: Optional[ElementHandle] = await chat.chatUI.element_handle(timeout=1500) \
                if isinstance(chat.chatUI, Locator) \
                else chat.chatUI if chat.chatUI is not None else None

            if handle is None:
                raise ChatClickError("Chat Object is Given None in WhatsApp chat loader / _click_chat")

            await handle.click(timeout=3500)
            return True
        except PlaywrightTimeoutError as e:
            raise ChatClickError("Failed to click chat in time.") from e
        except TweakioError as e:
            raise ChatClickError("Error in click the given chat.") from e

    @staticmethod
    async def is_unread(chat: Optional[whatsapp_chat]) -> int:
        """
        Returns:
        1 → chat has actual unread messages (numeric badge),
        0 → manually marked as unread (no numeric badge) or none,
        """
        try:
            if chat is None:
                raise ChatNotFoundError("none passed , expected chat in is_unread")

            handle: ElementHandle = await chat.chatUI.element_handle(timeout=1500) \
                if isinstance(chat.chatUI, Locator) else chat.chatUI

            unread_Badge = await handle.query_selector("[aria-label*='unread']")
            if unread_Badge:
                number_span = await unread_Badge.query_selector("span")
                if number_span:
                    text = (await number_span.inner_text()).strip()
                    if text.isdigit(): return 1
            return 0
        except TweakioError as e:
            raise ChatUnreadError("Error in is_unread checking") from e

    async def do_unread(self, chat: Optional[whatsapp_chat]) -> bool:
        """
        Marks the given chat as unread by simulating right-click and selecting 'Mark as unread'.
        If already unread, logs info instead of failing.
        """
        page = self.page

        if chat is None:
            raise ChatNotFoundError("none passed , expected chat in do_unread")

        try:
            chat_handle: ElementHandle = await chat.chatUI.element_handle(timeout=1500) \
                if isinstance(chat.chatUI, Locator) else chat.chatUI

            if chat.chatUI is None:
                raise ChatError("chat UI not initialized")

            # Right-click on chat
            await chat_handle.click(button="right")
            await page.wait_for_timeout(random.randint(1300, 2500))  # 1.3s to 2.5s

            # Get the application menu as ElementHandle
            menu = await page.query_selector("role=application")
            if not menu:
                raise ChatMenuError("No chat menu found -- do_unread")

            # Look for 'Mark as unread' option inside menu
            unread_option = await menu.query_selector("li >> text=/mark.*as.*unread/i")

            if unread_option:
                await unread_option.click(timeout=random.randint(1701, 2001))
                self.log.info("whatsApp chat loader / [do_unread] Marked as unread ✅")
            else:
                # Check if already unread
                read_option = await menu.query_selector("li >> text=/mark.*as.*read/i")
                if read_option:
                    self.log.info("whatsApp chat loader / [do_unread] Chat already unread")
                else:
                    self.log.info("whatsApp chat loader / [do_unread] Context menu option not found ❌")

            return True

        except PlaywrightTimeoutError as e:
            raise ChatUnreadError("Timeout while checking unread badge") from e

        except TweakioError as e:
            # Todo , recover() via WA Icon Click
            raise ChatUnreadError("Error in do_unread checking") from e
