"""
Test File for MessageProcessor From WA
"""
from playwright.async_api import Page

from src.WhatsApp.Message_Processor import MessageProcessor
import pytest
from unittest.mock import Mock, AsyncMock


def get_page()-> Page:
    """returns  a Mocked page obj """
    page = Mock()

    # Adding up properties


    return page