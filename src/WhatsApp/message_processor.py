"""
WhatsApp's Custom Message processor.
It will have in Extra as incoming and outgoing Message filters ,

"""
from __future__ import annotations

import logging
from typing import List, Optional

from playwright.async_api import Page

from sql_lite_storage import SQL_Lite_Storage
from src.Decorators.Chat_Click_decorator import ensure_chat_clicked
from src.Interfaces.messageprocessorinterface import MessageProcessorInterface
from src.MessageFilter import Filter
from src.WhatsApp.ChatProcessor import ChatProcessor
from src.WhatsApp.DefinedClasses.Chat import whatsapp_chat
from src.WhatsApp.DefinedClasses.Message import whatsapp_message
from src.WhatsApp.WebUISelector import WebSelectorConfig


class MessageProcessor(MessageProcessorInterface):

    def __init__(
            self,
            storage_obj: Optional[SQL_Lite_Storage],
            filter_obj: Optional[Filter],
            chat_processor: ChatProcessor,
            page: Page,
            log: logging.Logger,
            UIConfig: WebSelectorConfig
    ) -> None:
        super().__init__(
            storage_obj=storage_obj,
            filter_obj=filter_obj,
            log=log,
            page=page,
            UIConfig=UIConfig)
        self.chat_processor = chat_processor

    @staticmethod
    async def sort_messages(msgList: List[whatsapp_message], incoming: bool) -> List[whatsapp_message]:
        """
        Returns incoming messages sorted by direction.
        incoming : if true gives incoming messages , else false gives outgoing messages.
        """
        if not msgList: raise Exception("Cant Sort incoming messages/ List is Empty/None")
        if incoming:
            return [msg for msg in msgList if msg.Direction == "in"]
        return [msg for msg in msgList if msg.Direction == "out"]

    @ensure_chat_clicked(lambda self, chat: self.ChatProcessor._click_chat(chat))
    async def _get_wrapped_Messages(
            self,
            chat: whatsapp_chat,
            retry: int = 3, *args, **kwargs) \
            -> List[whatsapp_message]:

        wrapped_list: List[whatsapp_message] = []
        try:
            sc = self.UIConfig
            all_Msgs = await sc.messages()
            count = await all_Msgs.count()
            c = 0
            while c < retry and count == 0:
                all_Msgs = await sc.messages()
                count = await all_Msgs.count()
                c += 1

            if not count: raise Exception("Messages Not Found from UI / get wrapped messages / WA ")

            for i in range(count):
                msg = all_Msgs.nth(i)
                text = await sc.get_message_text(msg)
                data_id = await sc.get_dataID(msg)

                c2 = 0
                while not data_id and c2 < 3:
                    data_id = await sc.get_dataID(msg)
                    c2 += 1

                if not data_id:
                    self.log.error("Data ID in WA / get wrapped Messages , None/Empty. Skipping")
                    continue

                wrapped_list.append(
                    whatsapp_message(
                        MessageUI=msg,
                        Direction="in" if await msg.locator(".message-in").count() > 0 else "out",
                        raw_Data=text,
                        parent_chat=chat,
                        data_id=data_id
                        # Todo , Adding proper Type Checking Message. [txt , ing , vid, quoted]
                    )
                )
        except Exception as e:
            self.log.error(f"WA / [MessageProcessor] {e}", exc_info=True)
        return wrapped_list

    async def Fetcher(self, chat: whatsapp_chat, retry: int, *args, **kwargs) -> List[whatsapp_message]:
        msgList = await self._get_wrapped_Messages(chat, retry, *args, **kwargs)

        try:
            if self.storage:
                await self.storage.enqueue_insert(msgList)

            if self.filter:
                msgList = self.filter.apply(msgList)

            return msgList

        except Exception as e:
            self.log.error(f"WA / [MessageProcessor] / Fetcher {e}", exc_info=True)
            return msgList
