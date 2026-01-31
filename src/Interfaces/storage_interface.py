"""Storage Interface"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict

from src.Interfaces.message_interface import MessageInterface


class StorageInterface(ABC):
    def __init__(self, queue: asyncio.Queue, log: logging.Logger, **kwargs):
        """This Queue is Explicitly given to work as a Global Enqueue."""
        self.queue = queue
        self.log = log

    @abstractmethod
    def init_db(self, **kwargs): ...

    @abstractmethod
    def create_table(self, **kwargs): ...

    @abstractmethod
    def start_writer(self, **kwargs): ...

    @abstractmethod
    async def enqueue_insert(self, msgs: List[MessageInterface], **kwargs): ...

    @abstractmethod
    async def _insert_batch_internally(self, msgs: List[MessageInterface], **kwargs): ...

    @abstractmethod
    def check_message_if_exists(self, msg_id: str, **kwargs) -> bool: ...

    @abstractmethod
    def get_all_messages(self, **kwargs) -> List[Dict]: ...

    @abstractmethod
    async def close_db(self, **kwargs): ...
