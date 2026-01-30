import random
from typing import Union

from playwright.async_api import Page, ElementHandle, Locator, Position

from DepreciatedFiles__0_1_5_V_of_pypi import _Humanize as ha, _Media as med
from Custom_logger import logger
from src.WhatsApp import web_ui_config as sc


async def double_edge_click(page: Page, message: Union[ElementHandle, Locator]) -> bool:
    """For Replying , To double-click on the message"""
    try:
        if isinstance(message, Locator):
            message = await message.element_handle()  # Make it just before the clicking

        await message.scroll_into_view_if_needed(timeout=2000)
        condition = await sc.is_message_out(message)  # True = outgoing, False = incoming

        box = await message.bounding_box()
        if not box:
            return False

        rel_x = box["width"] * (0.2 if condition else 0.8)
        rel_y = box["height"] / 2

        await message.click(
            position=Position(x=rel_x, y=rel_y),
            click_count=2,
            delay=random.randint(38, 69),
            timeout=3000
        )

        # small pause to let UI react
        await page.wait_for_timeout(timeout=500)
        return True

    except Exception as e:
        logger.error(f"[double_edge_click] Error: {e}")
        return False


async def _reply_(page: Page, message: Union[ElementHandle, Locator], text: str, retry: int = 3) -> bool:
    """
    Core async function to type a reply into the message box without sending.

    Handles retries automatically on failure.

    Args:
        page (Page): Playwright page object.
        message (ElementHandle | Locator): Message element to reply to.
        text (str): Message text to type.
        retry (int): Current retry count.

    Returns:
        bool: True if typing succeeded, False otherwise.
    """
    try:
        await double_edge_click(page, message)

        inBox = sc.message_box(page)
        await inBox.click(timeout=3000)

        await ha.human_send(page, element=await inBox.element_handle(timeout=1000), text=text)
        return True

    except Exception as e:
        if retry != 0:
            return await _reply_(page, message, text, retry - 1)
        logger.error(f"[_reply_] Failed after retry // {e}", exc_info=True)
        return False


async def reply(
        page: Page,
        element: Union[ElementHandle, Locator],
        text: str) -> None:
    """
    Async function to reply to a message and automatically press Enter.

    Args:
        page (Page): Playwright page object.
        element (ElementHandle | Locator): Message element to reply to.
        text (str): Message text to send.
    """
    success = await _reply_(page, element, text)
    if success:
        await page.keyboard.press("Enter")
    else:
        logger.error("[reply] Failed to reply, Enter not pressed.", exc_info=True)


async def reply_media(
        page: Page,
        message: ElementHandle,
        text: str,
        file: list[str],
        mediatype: str = "doc",
        send_type: str = "add") -> None:
    """
    Sends a reply message with optional media attachment.

    Types the text first, then attaches media, and finally sends the message.
    Supports two sending types:
        - 'add': normal file attach via AddMedia
        - 'inject': direct file injection via InjectMedia

    Args:
        page (Page): Playwright page object.
        message (ElementHandle): Message element to reply to.
        text (str): Text to type before sending media.
        file (list[str]): List of file paths to attach.
        mediatype (str): Type of media ('doc', 'image', 'audio', etc.).
        send_type (str): 'add' or 'inject' for different media injection methods.
    """
    success = await _reply_(page, message, text)
    if success:
        if send_type == "inject":
            await med.InjectMedia(page=page, files=file, mediatype=mediatype)
        else:
            await med.AddMedia(page=page, file=file[0], mediatype=mediatype)

        await page.wait_for_timeout(random.randint(1123, 1491))
        await page.keyboard.press("Enter")
    else:
        await page.keyboard.press("Escape", delay=random.randint(701, 893))
        await page.keyboard.press("Escape", delay=random.randint(701, 893))
        logger.warning("[reply_media] Failed to reply with media, Escaped out.", exc_info=True)
