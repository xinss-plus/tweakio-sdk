from __future__ import annotations

import asyncio
import logging
import random
import re
from pathlib import Path

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError, Locator

import directory as dirs
from src.Exceptions.whatsapp import LoginError
from src.Interfaces.login_interface import LoginInterface
from src.WhatsApp.web_ui_config import WebSelectorConfig


class Login(LoginInterface):
    """WhatsApp Web Login Handler (QR / Code Based)"""

    def __init__(
            self,
            page: Page,
            UIConfig: WebSelectorConfig,
            log: logging.Logger
    ) -> None:
        super().__init__(page=page, UIConfig=UIConfig, log=log)
        if page is None:
            raise ValueError("page must not be None")

    async def is_login_successful(self) -> bool:
        # Will be implemented later
        return False

    async def login(self, **kwargs) -> bool:
        """
        This is Login File for WhatsApp.

        Login to WhatsApp Web supports two authentication routes:

        1) QR-Based Login
            - Requires scanning a QR code from a mobile device.
            - Used when login_prefer = 0.

        2) Code-Based Login
            - Login using phone number and country selection.
            - A temporary login code is generated on the screen.
            - Used when login_prefer = 1 (default).

        Parameters:
        -----------
        number:
            Phone number for the WhatsApp account.
            Example: 983283xxxx (country code included separately)

        country:
            Country name of the phone number.
            Example: India, india, Japan

        login_prefer:
            0 → QR-based login
            1 → Code-based login (default)

        page:
            Playwright Page object.
            Must be created before invoking login.

        storage_file_path:
            Path to browser storage state.
            Used to persist login session (cookies, local storage).

        override_login:
            If False:
                Uses existing storage file if present.
            If True:
                Forces fresh login and deletes old storage state.

        Behavior:
        ---------
        - Navigates to https://web.whatsapp.com
            - If storage state exists and override_login is False:
                Login is skipped.
            - Otherwise:
                Performs login based on selected method.
            - On successful login:
                Storage state is saved for future reuse.

        Returns:
        --------
        True  → Login successful
        False → Login failed in controlled scenarios
        Raises specific exceptions for invalid states.
        """

        method: int | None = kwargs.get("method")
        wait_time: int = kwargs.get("wait_time", 180_000)
        link: str  = kwargs.get("url") or "https://web.whatsapp.com"
        number: int | None = kwargs.get("number")
        country: str | None = kwargs.get("country")
        save_path: Path = kwargs.get("save_path", dirs.storage_state_file)

        try:
            await self.page.goto(link, timeout=60_000)
            await self.page.wait_for_load_state("networkidle", timeout=50_000)

            # Todo , check if the given link is correct or not .
        except PlaywrightTimeoutError as e:
            raise LoginError("Timeout while loading WhatsApp Web") from e

        if save_path.is_file() and save_path.stat().st_size > 0:
            self.log.info("Using existing WhatsApp session storage.")
            return True

        if method == 0:
            return await self.__qr_login(wait_time)
        if method == 1:
            return await self.__code_login(number, country)

        raise LoginError("Invalid login method. Use method=0 (QR) or method=1 (Code).")

    async def __qr_login(self, wait_time: int) -> bool:
        canvas = self.UIConfig.qr_canvas()
        self.log.info("Waiting for QR scan (%s seconds)...", wait_time // 1000)

        try:
            await self.UIConfig.chat_list().wait_for(
                timeout=wait_time,
                state="visible"
            )
            if await canvas.is_visible():
                raise LoginError("QR not scanned within allowed time.")
            return True
        except PlaywrightTimeoutError as e:
            raise LoginError("QR login timeout.") from e

    async def __code_login(self, number: int | None, country: str | None) -> bool:
        if not number or not country:
            raise LoginError("Both number and country are required for code login.")

        self.log.info("Starting code-based login...")

        btn = self.page.get_by_role(
            "button",
            name=re.compile("log.*in.*phone number", re.I)
        )
        if await btn.count() == 0:
            raise LoginError("Login-with-phone-number button not found.")

        try:
            await btn.click(timeout=3000)
            await self.page.wait_for_load_state("networkidle", timeout=10_000)
        except PlaywrightTimeoutError as e:
            raise LoginError("Failed to open phone login screen.") from e

        # Country selection
        ctl = self.page.locator("button:has(span[data-icon='chevron'])")
        if await ctl.count() == 0:
            raise LoginError("Country selector not found.")

        await ctl.click(timeout=3000)
        await self.page.keyboard.type(country, delay=random.randint(80, 120))
        await asyncio.sleep(1)

        countries: Locator = self.page.get_by_role("listitem").locator("button")
        if await countries.count() == 0:
            raise LoginError(f"No countries found for input: {country}")

        def normalize(name: str) -> str:
            return "".join(c for c in name if c.isalpha() or c.isspace()).lower().strip()

        selected = False
        for i in range(await countries.count()):
            el = countries.nth(i)
            name = normalize(await el.inner_text())
            if name == country.lower():
                await el.click(timeout=3000)
                selected = True
                break

        if not selected:
            raise LoginError(f"Country '{country}' not selectable.")

        # Phone number
        inp = self.page.locator("form >> input")
        if await inp.count() == 0:
            raise LoginError("Phone number input not found.")

        await inp.type(str(number), delay=random.randint(80, 120))
        await self.page.keyboard.press("Enter")

        # Login code
        code_el = self.page.locator("div[data-link-code]")
        try:
            await code_el.wait_for(timeout=10_000)
            code = await code_el.get_attribute("data-link-code")
            if not code:
                raise LoginError("Login code missing.")
            self.log.info("WhatsApp Login Code: %s", code)
        except PlaywrightTimeoutError as e:
            raise LoginError("Timeout while waiting for login code.") from e

        return True

    async def logout(self, **kwargs) -> bool:
        # Will be implemented later
        return False
