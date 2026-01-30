"""
WhatsApp based Chat Loader
"""
from __future__ import annotations

import logging
import random
from typing import Dict, List, Optional

from playwright.async_api import Page, ElementHandle, Locator

from src.Exceptions import ChatNotFoundError, ChatClickError
from src.Interfaces.chatprocessorinterface import ChatProcessorInterface
from src.WhatsApp.WebUISelector import WebSelectorConfig
from src.WhatsApp.DefinedClasses.Chat import whatsapp_chat


# Todo , add the paths for chatLoaderInterface , ChatInterface
class ChatProcessor(ChatProcessorInterface):
    """WhatsApp's Custom Chat processor """

    # Todo About the capabilities adding dynamically via functions and other Loaders providing comparison

    def __init__(self, page: Page, log: logging.Logger, UIConfig : WebSelectorConfig) -> None:
        super().__init__(page=page, log=log, UIConfig=UIConfig)
        self.capabilities: Dict[str, bool] = {}

    async def fetch_chats(self, limit: int = 5, retry: int = 5) -> List[whatsapp_chat]:
        """Fetching chats in the loaded JS UI of web page of WhatsApp"""
        try:
            ChatList: List[whatsapp_chat] = await self._get_Wrapped_Chat(limit=limit, retry=retry)

            if not ChatList:
                self.log.error(f"Chat not found.")
                raise ChatNotFoundError("Chats Not Found on the Page.")

            return ChatList
        except Exception as e:
            self.log.critical(f"[WA / chat_processor] Error: {e}", exc_info=True)
            return []

    async def _get_Wrapped_Chat(self, limit: int, retry: int) -> List[whatsapp_chat]:
        """List Based Raw data of chats"""
        try:
            sc = self.UIConfig
            chats = sc.chat_items()
            wrapped: List[whatsapp_chat] = []
            counter = 0
            while not (await chats.count()) and counter < retry:
                chats = sc.chat_items()
                await  page.wait_for_timeout(1000)
                counter += 1

            count = await chats.count()
            if not count: return wrapped

            minimum = min(count, limit)
            for i in range(minimum):
                wrapperChat = whatsapp_chat(
                    chatUI=chats.nth(i),
                    chatName= await sc.getChatName(chats.nth(i))
                )
                wrapped.append(wrapperChat)

            return wrapped
        except Exception as e:
            self.log.error(f"[WA / chat_processor] Error: {e}", exc_info=True)
            return []

#-------------------------------------------

    async def _click_chat(self, chat: Optional[whatsapp_chat]) -> bool:
        """Chat Clicker to open."""
        try:
            #---------------------
            # Todo , add check if chat is None
            #---------------------

            handle: Optional[ElementHandle] = await chat.chatUI.element_handle(timeout=1500) \
                if isinstance(chat.chatUI, Locator) \
                else chat.chatUI if chat.chatUI is not None else None
            # Todo Use ErrorTrack Class
            if handle is None: 
                raise ChatClickError("Chat Object is Given None in WhatsApp chat loader / _click_chat")

            await handle.click(timeout=3500)
            return True
        except Exception as e:
            self.log.error(f"WA / chat_processor / click_chat Error: {e}", exc_info=True)
            return False

    async def is_unread(self, chat: Optional[whatsapp_chat]) -> int:
        """
        Returns:
        1 → chat has actual unread messages (numeric badge),
        0 → manually marked as unread (no numeric badge) or none,
        -1 → error occurred
        """
        try:
            # Todo , Implement Error Class that can trace the Function Chain by itself
            if chat is None:
                raise ValueError("WhatsAPP Chat Object is Given None in WhatsApp chat loader / is_unread")

            handle: ElementHandle = await chat.chatUI.element_handle(timeout=1500) \
                if isinstance(chat.chatUI, Locator) else chat.chatUI

            unread_Badge = await handle.query_selector("[aria-label*='unread']")
            if unread_Badge:
                number_span = await unread_Badge.query_selector("span")
                if number_span:
                    text = (await number_span.inner_text()).strip()
                    if text.isdigit(): return 1
            return 0
        except Exception as e:
            self.log.error(f"WA / chat_processor / is_unread Error: {e}", exc_info=True)
            return -1

    async def do_unread(self, chat: Optional[whatsapp_chat]) -> bool:
        """
        Marks the given chat as unread by simulating right-click and selecting 'Mark as unread'.
        If already unread, logs info instead of failing.
        """
        try:
            if chat is None:
                raise ValueError("WhatsAPP Chat Object is Given None in WhatsApp chat loader / do_unread")

            chat_handle: ElementHandle = await chat.chatUI.element_handle(timeout=1500) \
                if isinstance(chat.chatUI, Locator) else chat.chatUI

            page = self.page
            if not chat_handle:
                self.log.warning("whatsApp chat loader / [do_unread] Chat handle not found")
                return False

            # Right-click on chat
            await chat_handle.click(button="right")
            await page.wait_for_timeout(random.randint(1300, 2500))  # 1.3s to 2.5s

            # Get the application menu as ElementHandle
            menu = await page.query_selector("role=application")
            if not menu:
                raise Exception("whatsApp chat loader / [do_unread] , App Menu not found")

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
        except Exception as e:
            self.log.error(f"whatsapp chat loader /  do_unread Error: {e}", exc_info=True)
            # Todo Adding Whatsapp Specific Util to click WA icon to reset the do_unread Process
            return False
