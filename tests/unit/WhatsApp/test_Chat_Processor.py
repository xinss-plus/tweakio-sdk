"""
Unit tests for Chat_Processor class.

This module demonstrates how to mock external dependencies like Playwright's Page
and Python's Logger for testing Chat_Processor in isolation.
"""

import logging
from unittest.mock import Mock, AsyncMock, patch

import pytest
from playwright.async_api import Page, Locator, ElementHandle

from src.WhatsApp.Chat_Processor import chat_processor
from src.WhatsApp.DefinedClasses.Chat import whatsapp_chat


# ============================================================================
# FIXTURES - Reusable Mock Objects
# ============================================================================

def get_mock_logger():
    """Create a mock logger for testing.
    
    This mock logger tracks all log calls without actually logging to console.
    You can assert on log calls like: mock_logger.error.assert_called_once()
    """
    logger = Mock(spec=logging.Logger)
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    logger.critical = Mock()
    return logger


def get_mock_page() -> Page:
    """Creates a Mocked playwright page Object.
    Also adds a mock Locator for the page.
    """
    page = AsyncMock(spec=Page)
    page.locator = AsyncMock(spec=Locator)
    page.wait_for_timeout = AsyncMock()
    page.click = AsyncMock()
    page.query_selector = AsyncMock()
    return page


@pytest.mark.asyncio
@patch("src.WhatsApp.Chat_Processor.sc")
async def test_get_wrapped_chat_with_data(mock_sc):
    """Test _get_Wrapped_Chat returns 2 chat objects."""

    # Setup mock locator
    mock_locator = AsyncMock(spec=Locator)
    mock_locator.count = AsyncMock(return_value=2)

    # mock elements that nth() will return
    mock_element_0 = AsyncMock(spec=ElementHandle)
    mock_element_1 = AsyncMock(spec=ElementHandle)

    mock_locator.nth = Mock(side_effect=lambda i: [mock_element_0, mock_element_1][i])

    mock_sc.chat_items = Mock(return_value=mock_locator)

    async def get_chat_name_side_effect(element):
        """Mock the getChatName"""
        if element == mock_element_0:
            return "Chat 1"
        elif element == mock_element_1:
            return "Chat 2"
        return "Unknown"

    mock_sc.getChatName = AsyncMock(side_effect=get_chat_name_side_effect)

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    chats = await p._get_Wrapped_Chat(limit=2, retry=2)

    assert len(chats) == 2
    assert chats[0].chatName == "Chat 1"
    assert chats[1].chatName == "Chat 2"

    mock_locator.nth.assert_any_call(0)
    mock_locator.nth.assert_any_call(1)


@pytest.mark.asyncio
@patch("src.WhatsApp.Chat_Processor.sc")
async def test_get_wrapped_chat_with_no_data(mock_sc):
    """Test _get_Wrapped_Chat returns empty list when no chats found."""

    mock_locator = AsyncMock(spec=Locator)
    mock_locator.count = AsyncMock(return_value=0)

    mock_sc.chat_items = Mock(return_value=mock_locator)

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    chats = await p._get_Wrapped_Chat(limit=2, retry=2)

    assert len(chats) == 0
    assert chats == []


@pytest.mark.asyncio
async def test_fetch_chats():
    # chat obj mock
    mock_whatsapp_chat_0 = Mock(spec=whatsapp_chat)
    mock_whatsapp_chat_1 = Mock(spec=whatsapp_chat)

    # mock get_wrapped_chat
    mock_wrappedChats = AsyncMock(return_value=[mock_whatsapp_chat_0, mock_whatsapp_chat_1])

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    p._get_Wrapped_Chat = mock_wrappedChats
    data = await p.fetch_chats(limit=2, retry=2)

    assert data == [mock_whatsapp_chat_0, mock_whatsapp_chat_1]

    # Mock empty dataset 
    p._get_Wrapped_Chat = AsyncMock(return_value=[])
    data = await p.fetch_chats(limit=2, retry=2)
    assert data == []


@pytest.mark.asyncio
async def test_click_chat():
    """Test _click_chat successfully clicks a chat."""
    # Create mock chat object
    mock_chat = Mock(spec=whatsapp_chat)

    # Create mock element that will be returned by element_handle
    mock_element = AsyncMock()
    mock_element.click = AsyncMock()

    # Setup chatUI as Locator with element_handle method
    mock_chat.chatUI = AsyncMock(spec=Locator)
    # ✅ FIXED: element_handle is a METHOD that returns an element
    mock_chat.chatUI.element_handle = AsyncMock(return_value=mock_element)

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())

    # Test successful click
    check = await p._click_chat(chat=mock_chat)
    assert check == True

    # Verify calls
    mock_chat.chatUI.element_handle.assert_called_once()
    mock_element.click.assert_called_once()


@pytest.mark.asyncio
async def test_click_chat_with_none():
    """Test _click_chat handles None chat gracefully."""
    p = chat_processor(page=get_mock_page(), log=get_mock_logger())

    # Test with None chat
    check = await p._click_chat(chat=None)
    assert check == False


@pytest.mark.asyncio
async def test_is_unread():
    """Test is_unread returns 1 when chat has numeric badge."""
    # Create mock chain from innermost to outermost
    mock_number_span = AsyncMock()
    mock_number_span.inner_text = AsyncMock(return_value="2")

    mock_unread_badge = AsyncMock()
    mock_unread_badge.query_selector = AsyncMock(return_value=mock_number_span)

    mock_handle = AsyncMock()
    mock_handle.query_selector = AsyncMock(return_value=mock_unread_badge)

    mock_chat = Mock(spec=whatsapp_chat)
    mock_chat.chatUI = AsyncMock(spec=Locator)
    mock_chat.chatUI.element_handle = AsyncMock(return_value=mock_handle)

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    check = await p.is_unread(chat=mock_chat)

    assert check == 1


@pytest.mark.asyncio
async def test_is_unread_with_empty_text():
    """Test is_unread returns 0 when manually marked unread (no number)."""
    mock_number_span = AsyncMock()
    mock_number_span.inner_text = AsyncMock(return_value="")  # Empty text

    mock_unread_badge = AsyncMock()
    mock_unread_badge.query_selector = AsyncMock(return_value=mock_number_span)

    mock_handle = AsyncMock()
    mock_handle.query_selector = AsyncMock(return_value=mock_unread_badge)

    mock_chat = Mock(spec=whatsapp_chat)
    mock_chat.chatUI = AsyncMock(spec=Locator)
    mock_chat.chatUI.element_handle = AsyncMock(return_value=mock_handle)

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    check = await p.is_unread(chat=mock_chat)

    assert check == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("inner_text_val, expected", [
    ("5", 1),  # Numeric badge
    ("10", 1),  # Different number
    ("", 0),  # Empty string (manually marked)
    ("  ", 0),  # Whitespace only
])
async def test_is_unread_with_different_badge_texts(inner_text_val, expected):
    """Test is_unread returns correct values for different badge text scenarios."""
    # Setup mock chain
    mock_number_span = AsyncMock()
    mock_number_span.inner_text = AsyncMock(return_value=inner_text_val)  # ✅ Fixed: No nested AsyncMock

    mock_unread_badge = AsyncMock()
    mock_unread_badge.query_selector = AsyncMock(return_value=mock_number_span)

    mock_handle = AsyncMock()
    mock_handle.query_selector = AsyncMock(return_value=mock_unread_badge)

    mock_chat = Mock(spec=whatsapp_chat)
    mock_chat.chatUI = AsyncMock(spec=Locator)
    mock_chat.chatUI.element_handle = AsyncMock(return_value=mock_handle)

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    result = await p.is_unread(chat=mock_chat)

    assert result == expected


@pytest.mark.asyncio
async def test_is_unread_no_badge_found():
    """Test is_unread returns 0 when no unread badge exists."""
    mock_handle = AsyncMock()
    mock_handle.query_selector = AsyncMock(return_value=None)  # No badge found

    mock_chat = Mock(spec=whatsapp_chat)
    mock_chat.chatUI = AsyncMock(spec=Locator)
    mock_chat.chatUI.element_handle = AsyncMock(return_value=mock_handle)

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    result = await p.is_unread(chat=mock_chat)

    assert result == 0


@pytest.mark.asyncio
async def test_is_unread_none_chat_returns_error():
    """Test is_unread returns -1 when chat is None."""
    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    result = await p.is_unread(chat=None)

    assert result == -1


@pytest.mark.asyncio
async def test_get_wrapped_chat_Exception():
    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    answer = await p._get_Wrapped_Chat(limit=3, retry=3)

    assert answer == []


@pytest.mark.asyncio
async def test_click_chat_None_handle():
    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    mock_chat = Mock(spec=whatsapp_chat)
    mock_chat.chatUI = AsyncMock(spec=Locator)
    mock_chat.chatUI.element_handle = AsyncMock(return_value=None)

    check = await p._click_chat(chat=mock_chat)

    assert check == False


@pytest.mark.asyncio
async def test_do_unread_no_chat_and_n0_chathandle():
    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    check = await p.do_unread(chat=None)
    assert check == False

    # Mock with None Chat handle
    mock_chat = Mock(spec=whatsapp_chat)
    mock_chat.chatUI = AsyncMock(spec=Locator)
    mock_chat.chatUI.element_handle = AsyncMock(return_value=None)
    check = await p.do_unread(chat=mock_chat)
    assert check == False


@pytest.mark.asyncio
async def test_do_unread_menu_not_found():
    """Test do_unread when menu (page.query_selector) returns None."""
    mock_chat = Mock(spec=whatsapp_chat)
    mock_chat.chatUI = AsyncMock(spec=Locator)
    mock_chat_handle = AsyncMock(spec=ElementHandle)
    mock_chat_handle.click = AsyncMock()
    mock_chat.chatUI.element_handle = AsyncMock(return_value=mock_chat_handle)

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    p.page.query_selector = AsyncMock(return_value=None)  # Menu not found

    check = await p.do_unread(chat=mock_chat)
    assert check == False


@pytest.mark.asyncio
async def test_do_unread_happy_path():
    """Test do_unread when unread option is found and clicked."""
    mock_chat = Mock(spec=whatsapp_chat)
    mock_chat.chatUI = AsyncMock(spec=Locator)
    mock_chat_handle = AsyncMock(spec=ElementHandle)
    mock_chat_handle.click = AsyncMock()
    mock_chat.chatUI.element_handle = AsyncMock(return_value=mock_chat_handle)

    # Setup menu with unread option
    mock_unread_option = AsyncMock()
    mock_unread_option.click = AsyncMock()

    mock_menu = AsyncMock()
    mock_menu.query_selector = AsyncMock(return_value=mock_unread_option)

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    p.page.query_selector = AsyncMock(return_value=mock_menu)

    check = await p.do_unread(chat=mock_chat)
    assert check == True

    mock_unread_option.click.assert_called_once()


@pytest.mark.asyncio
async def test_do_unread_already_unread():
    """Test do_unread when chat is already unread (else if branch)."""
    mock_chat = Mock(spec=whatsapp_chat)
    mock_chat.chatUI = AsyncMock(spec=Locator)
    mock_chat_handle = AsyncMock(spec=ElementHandle)
    mock_chat_handle.click = AsyncMock()
    mock_chat.chatUI.element_handle = AsyncMock(return_value=mock_chat_handle)

    # Setup: unread_option = None, but read_option exists
    mock_read_option = AsyncMock()

    mock_menu = AsyncMock()
    mock_menu.query_selector = AsyncMock(side_effect=[
        None,  # if Case
        mock_read_option  # Else Case
    ])

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    p.page.query_selector = AsyncMock(return_value=mock_menu)

    check = await p.do_unread(chat=mock_chat)
    assert check == True


@pytest.mark.asyncio
async def test_do_unread_no_options_found():
    """Test do_unread when neither unread nor read option found (else else branch)."""
    mock_chat = Mock(spec=whatsapp_chat)
    mock_chat.chatUI = AsyncMock(spec=Locator)
    mock_chat_handle = AsyncMock(spec=ElementHandle)
    mock_chat_handle.click = AsyncMock()
    mock_chat.chatUI.element_handle = AsyncMock(return_value=mock_chat_handle)

    # Setup: Both unread_option and read_option are None
    mock_menu = AsyncMock()
    mock_menu.query_selector = AsyncMock(return_value=None)

    p = chat_processor(page=get_mock_page(), log=get_mock_logger())
    p.page.query_selector = AsyncMock(return_value=mock_menu)

    check = await p.do_unread(chat=mock_chat)
    assert check == True
