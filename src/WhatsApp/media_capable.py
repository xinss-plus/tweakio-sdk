"""WhatsApp Customized Media operations, Derived from the Media Interface"""

from __future__ import annotations

import asyncio
import logging
import random
from pathlib import Path
from typing import Union

from playwright.async_api import Page, ElementHandle, Locator, FileChooser

from src.Interfaces.media_capable_interface import MediaCapableInterface, MediaType, FileTyped
from src.Interfaces.message_interface import MessageInterface
from src.Interfaces.web_ui_selector import WebUISelectorCapable


class MediaHandle(MediaCapableInterface):
    """WhatsApp media capable Obj Class"""

    def __init__(self, page: Page, log: logging.Logger, UIConfig: WebUISelectorCapable) -> None:
        super().__init__(page=page, log=log, UIConfig=UIConfig)

    async def menu_clicker(self):
        """Open WhatsApp menu for File sending selection"""
        try:
            menu_icon = await self.UIConfig.plus_rounded_icon(self.page).element_handle(timeout=1000)

            if not menu_icon:
                self.log.error("WA / menu_clicker /Menu Icon not found ", exc_info=True)
                return

            await menu_icon.click(timeout=3000)
            await asyncio.sleep(random.uniform(1.0, 1.5))
        except Exception as e:
            self.log.error(f"Error at WA / menu_clicker : {e}", exc_info=True)

            # Revert back to the condition .
            await self.page.keyboard.press("Escape", delay=0.5)

    async def add_media(self, mtype: MediaType, Message: MessageInterface, file: FileTyped, **kwargs) -> bool:
        # Open the Menu
        await self.menu_clicker()
        try:
            # Ready the target option
            target = await self._getOperational(mtype=mtype)
            target = await target.element_handle(timeout=1000)

            if not await target.is_visible():
                self.log.error(f"Attach option for '{mtype}' not visible", exc_info=True)
                raise Exception("WA / add_media / Attach option not visible")

            # Mock the File option selection
            with await self.page.expect_file_chooser() as fc:
                await target.click(timeout=3000)
            chooser: FileChooser = fc.value

            # file.uri , that path must be existed in the system scope and file designated should be there
            p = Path(file.uri)
            if not p.exists():
                self.log.error(f"File not found: {file.uri}", exc_info=True)
                return False

            await chooser.set_files(str(p.resolve()))
            self.log.info(f" --- Sent {str(p.resolve())} , [Mtype] = [{mtype}] ")
            return True
        except Exception as e:
            self.log.error(f"Error at WA / add_media : {e}", exc_info=True)
            return False

    async def _getOperational(self, mtype: MediaType) -> Union[ElementHandle, Locator]:
        sc = self.UIConfig
        if mtype in (MediaType.TEXT, MediaType.IMAGE, MediaType.VIDEO):
            return sc.photos_videos(self.page)

        if mtype == MediaType.AUDIO:
            return sc.audio(self.page)

        return sc.document(self.page)
