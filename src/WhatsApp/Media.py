"""WhatsApp Customized Media operations, Derived from the Media Interface"""

from __future__ import annotations

from playwright.async_api import Page

from src.Interfaces.Media_Capable_Interface import MediaCapableInterface, MediaType, FileTyped
from src.Interfaces.Message_Interface import message_interface


class Media(MediaCapableInterface):

    def __init__(self, page : Page):
        super().__init__(page=page)

    async def media_add(self, mtype: MediaType, Message: message_interface, file: FileTyped) -> bool:
        pass
