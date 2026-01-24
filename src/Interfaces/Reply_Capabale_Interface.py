from abc import ABC, abstractmethod
from src.Interfaces.Message_Interface import message_interface
class ReplyCapabaleInterface(ABC):
    @abstractmethod
    async def reply(self, Message : message_interface):
        """Reply to that Message"""
        pass