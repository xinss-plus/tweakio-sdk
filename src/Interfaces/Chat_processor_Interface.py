"""
This is a Chat Loading Interface contract .
It will help give the Basic Functions like fetching and giving list of Chat Objs.
Ex : Fetch , wrappedChats , ChatClicker

Any Specific Function will be defined via Child Class as if those are platform Independent.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import ChatInterface

from Chat_Interface import chat_interface


class chat_processor_interface(ABC):
    """Chat Loader Interface"""
    capabilities: Dict[str, bool]

    @abstractmethod
    async def fetch_chats(self) -> List[chat_interface]:
        """Fetch and return limited chat objects"""
        pass

    @staticmethod
    @abstractmethod
    async def _click_chat(chat : Optional[chat_interface]) -> bool:
        """Click chat object"""
        pass

    @abstractmethod
    async def _get_Wrapped_Chat(self, *args, **kwargs) -> List[chat_interface]: pass
