"""
Login Interface for all Platform.
"""

from abc import ABC, abstractmethod

class LoginInterface(ABC):
    """All Must Implementable functions Interface"""
    @abstractmethod
    async def login(self, **kwargs) -> bool:
        """Login to the platform"""
        pass

    async def logout(self, **kwargs) -> bool:
        """Logouts the account from the platform"""
        pass

    async def is_login_successful(self, **kwargs) -> bool:
        """Check the login status"""
        pass