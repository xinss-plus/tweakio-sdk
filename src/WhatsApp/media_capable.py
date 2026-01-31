"""WhatsApp Customized Media operations, Derived from the Media Interface"""

from __future__ import annotations

import asyncio
import logging
import random
from pathlib import Path
from playwright.async_api import Page, Locator, FileChooser, TimeoutError as PlaywrightTimeoutError

from src.Exceptions.whatsapp import MenuError, MediaCapableError, WhatsAppError
from src.Interfaces.media_capable_interface import MediaCapableInterface, MediaType, FileTyped
from src.Interfaces.web_ui_selector import WebUISelectorCapable


class MediaCapable(MediaCapableInterface):
    """WhatsApp media capable Obj Class"""

    def __init__(self, page: Page, log: logging.Logger, UIConfig: WebUISelectorCapable) -> None:
        super().__init__(page=page, log=log, UIConfig=UIConfig)
        if self.page is None:
            raise ValueError("page must not be None")

    async def menu_clicker(self) -> None:
        """Open WhatsApp menu for File sending selection"""
        try:
            menu_icon = await self.UIConfig.plus_rounded_icon(self.page).element_handle(timeout=1000)

            if not menu_icon:
                raise MenuError("Menu Locator return None/Empty / menu_clicker / MediaCapable")

            await menu_icon.click(timeout=3000)
            await asyncio.sleep(random.uniform(1.0, 1.5))

        except PlaywrightTimeoutError as e:

            # Revert back to the condition .
            await self.page.keyboard.press("Escape", delay=0.5)

            raise MediaCapableError("Time out while clicking menu") from e

    async def add_media(self, mtype: MediaType, file: FileTyped, **kwargs) -> bool:
        # Open Menu
        await self.menu_clicker()
        try:
            target = await self._getOperational(mtype=mtype)
            if not await target.is_visible(timeout=3000):
                raise MediaCapableError("Attach option not visible")

            # File option selection
            with await self.page.expect_file_chooser() as fc:
                await target.click(timeout=3000)
            chooser: FileChooser = fc.value

            # file.uri , that path must be existed in the system scope and file designated should be there
            p = Path(file.uri)
            if not p.exists() or not p.is_file():
                raise MediaCapableError(f"Invalid file path: {file.uri}")

            # Set file
            await chooser.set_files(str(p.resolve()))
            self.log.debug(f" --- Sent {str(p.resolve())} , [Mtype] = [{mtype}] ")
            return True

        except PlaywrightTimeoutError as e:
            raise MediaCapableError("Timeout while resolving media option") from e

        except WhatsAppError as e:
            raise MediaCapableError("Unexpected Error in add_media") from e

    async def _getOperational(self, mtype: MediaType) -> Locator:
        sc = self.UIConfig
        if mtype in (MediaType.TEXT, MediaType.IMAGE, MediaType.VIDEO):
            return sc.photos_videos(self.page)

        if mtype == MediaType.AUDIO:
            return sc.audio(self.page)

        return sc.document(self.page)
