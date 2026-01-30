"""
Tweakio SDK Custom Exceptions

Hierarchy:
    TweakioError (Base)
    ├── ChatError
    │   ├── ChatNotFoundError
    │   └── ChatClickError
    ├── MessageError
    │   ├── MessageNotFoundError
    │   └── MessageDataError
    └── AuthenticationError
        └── QRNotScannedError
"""


class TweakioError(Exception):
    """Base exception for all Tweakio SDK errors"""
    pass


# Chat-related errors
class ChatError(TweakioError):
    """Base exception for chat-related errors"""
    pass


class ChatNotFoundError(ChatError):
    """Raised when a chat cannot be found"""
    pass


class ChatClickError(ChatError):
    """Raised when clicking a chat fails"""
    pass


# Message-related errors
class MessageError(TweakioError):
    """Base exception for message-related errors"""
    pass


class MessageNotFoundError(MessageError):
    """Raised when messages cannot be found"""
    pass


class MessageDataError(MessageError):
    """Raised when message data is invalid or missing"""
    pass


# Authentication errors
class AuthenticationError(TweakioError):
    """Base exception for authentication errors"""
    pass


class QRNotScannedError(AuthenticationError):
    """Raised when QR code is not scanned within timeout"""
    pass

# Filtering Errors
class MessageFilterError(TweakioError):
    """Base exception for message-related errors"""
    pass

# ReplyCapable Error
class ReplyCapableError(TweakioError):
    """Base exception for reply-related errors"""
    pass
