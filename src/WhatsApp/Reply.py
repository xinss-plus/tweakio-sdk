"""WhatsApp Customized Reply Module"""

from __future__ import annotations

from src.Interfaces.Message_Interface import message_interface
from src.Interfaces.Reply_Capabale_Interface import ReplyCapabaleInterface

class Reply(ReplyCapabaleInterface):

    async def reply(self, Message : message_interface):
        pass