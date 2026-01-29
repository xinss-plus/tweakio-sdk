"""
File to test Humanized Operations From WhatsApp.
"""
from typing import Union
from unittest.mock import AsyncMock, Mock

import pytest
from playwright.async_api import Page, ElementHandle, Locator

from src.WhatsApp.Humanized_Opeartions import Humanized_Operation
from tests.unit.WhatsApp.test_Chat_Processor import get_mock_logger


def get_page() -> Page:
    """Create mock Page object."""
    page = Mock(spec=Page)
    mock_keyboard = AsyncMock()
    mock_keyboard.type = AsyncMock()
    mock_keyboard.press = AsyncMock()
    page.keyboard = mock_keyboard
    return page


def get_humanized_class():
    """Create Humanized_Operation instance with mocks."""
    obj = Humanized_Operation(page=get_page(), log=get_mock_logger())
    return obj


@pytest.mark.asyncio
async def test_human_op_typing_with_no_source():
    """Test typing raises exception when no source provided."""
    obj = get_humanized_class()

    with pytest.raises(Exception, match="Wrong Method Assigned"):
        await obj.typing(text="test")


@pytest.mark.asyncio
async def test_human_op_typing_with_none_source():
    """Test typing raises exception when source is None."""
    obj = get_humanized_class()
    mess = "Wrong Method Assigned , need clickable_source in wa/ humanize / typing"

    with pytest.raises(Exception) as e:
        await obj.typing(text="test", source=None)

    assert str(e.value) == mess


@pytest.mark.asyncio
@pytest.mark.parametrize("text_len", [
    10,  # Less than 50 - uses keyboard.type
    60,  # Greater than 50 - uses clipboard
])
async def test_human_op_typing_normal_usage(text_len) -> None:
    """Test typing with different text lengths."""
    mock_text = "x\n" * text_len
    mock_source = AsyncMock(spec=Union[ElementHandle, Locator])

    # Mock Internal Flow
    mock_source.click = AsyncMock()
    mock_source.press = AsyncMock()
    mock_source.fill = AsyncMock()

    # Setup
    obj = get_humanized_class()
    check = await obj.typing(text=mock_text, source=mock_source)

    # Test
    assert check == True
    mock_source.click.assert_called_once()


@pytest.mark.asyncio
async def test_human_op_typing_falls_back_to_fill():
    """Test typing falls back to fill() when clicking fails."""
    mock_text = "test message"
    mock_source = AsyncMock(spec=Union[ElementHandle, Locator])

    # Make click fail to trigger fallback
    mock_source.click = AsyncMock(side_effect=Exception("Click failed"))
    mock_source.fill = AsyncMock()

    obj = get_humanized_class()
    check = await obj.typing(text=mock_text, source=mock_source)

    # Should still return True (fallback succeeded)
    assert check == True
    mock_source.fill.assert_called_once_with(mock_text)


@pytest.mark.asyncio
async def test_instant_fill_with_no_source():
    """Test _Instant_fill raises exception when source is None."""
    obj = get_humanized_class()

    with pytest.raises(Exception, match="need clickable_source"):
        await obj._Instant_fill(text="test", source=None)


@pytest.mark.asyncio
async def test_instant_fill_internal_exception_returns_false():
    obj = get_humanized_class()

    mock_source = AsyncMock(spec=Union[ElementHandle, Locator])
    mock_source.fill = AsyncMock(side_effect=Exception("Fill failed"))

    result = await obj._Instant_fill(text="test", source=mock_source)

    assert result == False
    mock_source.fill.assert_called_once()


@pytest.mark.asyncio
async def test_instant_fill_with_source():
    """Test _Instant_fill successfully fills and presses Enter."""
    obj = get_humanized_class()
    mock_source = AsyncMock(spec=Union[ElementHandle, Locator])
    mock_source.fill = AsyncMock()

    check = await obj._Instant_fill(text="test", source=mock_source)
    assert check == True

    mock_source.fill.assert_called_once_with("test")
    obj.page.keyboard.press.assert_called()
