"""
title: Playwright Web Automation
author: j4ckxyz
author_url: https://github.com/j4ckxyz
git_url: https://github.com/j4ckxyz/openwebui-playwright-tool
description: Comprehensive browser automation tool enabling AI models to navigate websites, interact with elements, extract data, and capture screenshots using Playwright.
required_open_webui_version: 0.4.0
requirements: playwright
version: 3.2.0
licence: MIT
"""

import json
import base64
import asyncio
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Literal, List
import os
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeoutError


class Tools:
    class Valves(BaseModel):
        BROWSER_TYPE: str = "chromium"  # chromium, firefox, webkit
        DEFAULT_TIMEOUT: int = 30000  # ms
        VIEWPORT_WIDTH: int = 1280
        VIEWPORT_HEIGHT: int = 720

    def __init__(self):
        self.valves = self.Valves()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def _ensure_browser(self):
        """Initialize browser if not already running (headless-only)."""
        if not self.playwright:
            self.playwright = await async_playwright().start()

        if not self.browser:
            browser_type = getattr(self.playwright, self.valves.BROWSER_TYPE)
            # Headless-only for reliability across servers/CI/OpenWebUI
            self.browser = await browser_type.launch(headless=True)

        if not self.context:
            self.context = await self.browser.new_context(
                viewport={
                    "width": self.valves.VIEWPORT_WIDTH,
                    "height": self.valves.VIEWPORT_HEIGHT,
                }
            )
            self.context.set_default_timeout(self.valves.DEFAULT_TIMEOUT)

        if not self.page:
            self.page = await self.context.new_page()

    # ---------- Core primitives ----------
    async def navigate_to_url(
        self,
        url: str,
        wait_until: Literal["load", "domcontentloaded", "networkidle"] = "load",
    ) -> str:
        try:
            await self._ensure_browser()
            response = await self.page.goto(url, wait_until=wait_until)
            return json.dumps(
                {
                    "status": "success",
                    "url": self.page.url,
                    "title": await self.page.title(),
                    "status_code": response.status if response else None,
                    "message": f"Navigated to {self.page.url}",
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "message": f"Navigation failed: {str(e)}",
                },
                indent=2,
            )

    async def get_page_text(self) -> str:
        try:
            await self._ensure_browser()
            text = await self.page.evaluate("() => document.body.innerText")
            return text
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)}, indent=2)

    async def get_page_html(self) -> str:
        try:
            await self._ensure_browser()
            return await self.page.content()
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)}, indent=2)

    async def click_element(
        self,
        selector: str,
        wait_for_navigation: bool = False,
    ) -> str:
        try:
            await self._ensure_browser()
            if wait_for_navigation:
                async with self.page.expect_navigation():
                    await self.page.click(selector)
                return json.dumps(
                    {
                        "status": "success",
                        "message": f"Clicked {selector} and navigated",
                        "navigated": True,
                        "new_url": self.page.url,
                    },
                    indent=2,
                )
            else:
                await self.page.click(selector)
                return json.dumps(
                    {
                        "status": "success",
                        "message": f"Clicked {selector}",
                        "navigated": False,
                    },
                    indent=2,
                )
        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "message": f"Failed to click {selector}: {str(e)}",
                },
                indent=2,
            )

    async def fill_input(
        self,
        selector: str,
        value: str,
        submit: bool = False,
    ) -> str:
        try:
            await self._ensure_browser()
            await self.page.fill(selector, value)
            if submit:
                await self.page.press(selector, "Enter")
            return json.dumps(
                {
                    "status": "success",
                    "message": f"Filled {selector} with text",
                    "submitted": submit,
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "message": f"Failed to fill {selector}: {str(e)}",
                },
                indent=2,
            )

    async def extract_elements(
        self,
        selector: str,
        attributes: str = "text,href",
        max_elements: int = 10,
    ) -> str:
        try:
            await self._ensure_browser()
            attr_list = [a.strip() for a in attributes.split(",") if a.strip()]
            elements = await self.page.query_selector_all(selector)
            results = []
            for element in elements[:max_elements]:
                element_data = {}
                for attr in attr_list:
                    if attr == "text":
                        element_data["text"] = await element.inner_text()
                    elif attr == "html":
                        element_data["html"] = await element.inner_html()
                    else:
                        element_data[attr] = await element.get_attribute(attr)
                results.append(element_data)
            return json.dumps(
                {"status": "success", "count": len(results), "elements": results},
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "message": f"Failed to extract elements: {str(e)}",
                },
                indent=2,
            )

    async def take_screenshot(
        self,
        full_page: bool = False,
        element_selector: Optional[str] = None,
    ) -> str:
        try:
            await self._ensure_browser()
            if element_selector:
                element = await self.page.query_selector(element_selector)
                if not element:
                    return json.dumps(
                        {"status": "error", "message": f"Element not found: {element_selector}"},
                        indent=2,
                    )
                screenshot_bytes = await element.screenshot(type="png")
            else:
                screenshot_bytes = await self.page.screenshot(type="png", full_page=full_page)
            base64_image = base64.b64encode(screenshot_bytes).decode("utf-8")
            data_uri = f"data:image/png;base64,{base64_image}"
            return json.dumps(
                {
                    "status": "success",
                    "image": data_uri,
                    "timestamp": datetime.now().isoformat(),
                    "message": "Screenshot captured",
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {"status": "error", "error": str(e), "message": f"Screenshot failed: {str(e)}"},
                indent=2,
            )

    async def execute_javascript(self, script: str) -> str:
        try:
            await self._ensure_browser()
            result = await self.page.evaluate(script)
            return json.dumps(
                {"status": "success", "result": result, "result_type": type(result).__name__},
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "message": f"JavaScript execution failed: {str(e)}",
                },
                indent=2,
            )

    async def wait_for_element(
        self,
        selector: str,
        state: Literal["attached", "detached", "visible", "hidden"] = "visible",
        timeout: int = 30000,
    ) -> str:
        try:
            await self._ensure_browser()
            await self.page.wait_for_selector(selector, state=state, timeout=timeout)
            return json.dumps(
                {
                    "status": "success",
                    "message": f"Element {selector} reached state: {state}",
                    "state": state,
                },
                indent=2,
            )
        except PlaywrightTimeoutError:
            return json.dumps(
                {
                    "status": "error",
                    "error": "Timeout",
                    "message": f"Element {selector} did not reach state {state} within {timeout}ms",
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {"status": "error", "error": str(e), "message": f"Wait failed: {str(e)}"},
                indent=2,
            )

    async def search_google(self, query: str, num_results: int = 5) -> str:
        try:
            await self._ensure_browser()
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            await self.page.goto(search_url, wait_until="networkidle")
            await self.page.wait_for_timeout(1000)
            results = []
            search_results = await self.page.query_selector_all("div.g")
            for result in search_results[:num_results]:
                try:
                    title_elem = await result.query_selector("h3")
                    link_elem = await result.query_selector("a")
                    snippet_elem = await result.query_selector("div.VwiC3b")
                    if title_elem and link_elem:
                        results.append(
                            {
                                "title": await title_elem.inner_text(),
                                "url": await link_elem.get_attribute("href"),
                                "snippet": await snippet_elem.inner_text() if snippet_elem else "",
                            }
                        )
                except Exception:
                    continue
            return json.dumps(
                {"status": "success", "query": query, "count": len(results), "results": results},
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "message": f"Google search failed: {str(e)}",
                },
                indent=2,
            )

    async def scroll_page(self, direction: Literal["up", "down", "top", "bottom"] = "down") -> str:
        try:
            await self._ensure_browser()
            if direction == "top":
                script = "window.scrollTo(0, 0)"
            elif direction == "bottom":
                script = "window.scrollTo(0, document.body.scrollHeight)"
            elif direction == "up":
                script = "window.scrollBy(0, -window.innerHeight)"
            else:  # down
                script = "window.scrollBy(0, window.innerHeight)"
            await self.page.evaluate(script)
            return json.dumps(
                {"status": "success", "message": f"Scrolled {direction}", "direction": direction},
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {"status": "error", "error": str(e), "message": f"Scroll failed: {str(e)}"},
                indent=2,
            )

    async def close_browser(self) -> str:
        try:
            if self.page:
                await self.page.close()
                self.page = None
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            return json.dumps({"status": "success", "message": "Browser closed and resources cleaned up"}, indent=2)
        except Exception as e:
            return json.dumps(
                {"status": "error", "error": str(e), "message": f"Cleanup failed: {str(e)}"},
                indent=2,
            )

    # ---------- High-level multi-step helpers ----------
    async def click_by_text(
        self,
        text: str,
        exact: bool = False,
        wait_for_navigation: bool = True,
        timeout: int = 10000,
    ) -> str:
        """
        Click the first element containing the given text using Playwright's text engine.
        Useful for links/buttons like "Read more", "Accept", etc.
        """
        try:
            await self._ensure_browser()
            locator = self.page.get_by_text(text, exact=exact)
            await locator.first.wait_for(state="visible", timeout=timeout)
            if wait_for_navigation:
                async with self.page.expect_navigation():
                    await locator.first.click()
                return json.dumps(
                    {
                        "status": "success",
                        "message": f"Clicked text '{text}' and navigated",
                        "navigated": True,
                        "new_url": self.page.url,
                    },
                    indent=2,
                )
            else:
                await locator.first.click()
                return json.dumps(
                    {"status": "success", "message": f"Clicked text '{text}'", "navigated": False},
                    indent=2,
                )
        except Exception as e:
            return json.dumps(
                {"status": "error", "error": str(e), "message": f"Failed to click text '{text}': {str(e)}"},
                indent=2,
            )

    async def accept_cookies(self) -> str:
        """Best-effort cookie banner accept based on common button texts."""
        try:
            await self._ensure_browser()
            candidates = [
                "Accept all",
                "Accept All",
                "I agree",
                "Agree",
                "Accept",
                "Got it",
                "Allow all",
            ]
            clicked = False
            for label in candidates:
                try:
                    loc = self.page.get_by_role("button", name=label)
                    if await loc.count() > 0:
                        await loc.first.click(timeout=1000)
                        clicked = True
                        break
                except Exception:
                    continue
            return json.dumps({"status": "success", "clicked": clicked}, indent=2)
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)}, indent=2)

    async def read_page(
        self,
        main_selectors: str = "article, main, .post-content, .entry-content, .post, .content",
        include_html: bool = False,
        max_chars: int = 20000,
    ) -> str:
        """
        Extracts structured content from the current page: url, title, meta description, and main text.
        Heuristically targets typical blog containers, falls back to body text.
        """
        try:
            await self._ensure_browser()
            url = self.page.url
            title = await self.page.title()
            # meta description
            try:
                desc = await self.page.locator('meta[name="description"]').first.get_attribute("content")
            except Exception:
                desc = None

            # find main content element
            locator = self.page.locator(
                ",".join([s.strip() for s in main_selectors.split(",") if s.strip()])
            )
            text_content = None
            html_content = None
            if await locator.count() > 0:
                text_content = await locator.first.inner_text()
                if include_html:
                    html_content = await locator.first.inner_html()
            else:
                text_content = await self.page.evaluate("() => document.body.innerText")
                if include_html:
                    html_content = await self.page.content()

            if text_content is None:
                text_content = ""
            text_content = text_content.strip()
            if len(text_content) > max_chars:
                text_content = text_content[:max_chars]

            result = {
                "status": "success",
                "url": url,
                "title": title,
                "description": desc,
                "text": text_content,
                "length": len(text_content),
            }
            if include_html and html_content is not None:
                result["html"] = html_content
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(
                {"status": "error", "error": str(e), "message": f"Failed to read page: {str(e)}"},
                indent=2,
            )

    async def open_latest_post(
        self,
        base_url: str,
        wait_until: Literal["load", "domcontentloaded", "networkidle"] = "load",
        post_link_selectors: str = "article a, .post a, h2 a, h3 a",
        also_try_read_more: bool = True,
        read_include_html: bool = False,
        max_chars: int = 20000,
    ) -> str:
        """
        Multi-step flow: navigate to blog home, optionally accept cookies, click the first likely post link,
        then return structured content from the post page (url, title, description, main text).
        """
        try:
            await self._ensure_browser()
            await self.page.goto(base_url, wait_until=wait_until)
            # Try accept cookies non-blocking
            try:
                await self.page.wait_for_timeout(500)
                await self.accept_cookies()
            except Exception:
                pass

            # Try selectors in order
            link = None
            selectors = [s.strip() for s in post_link_selectors.split(",") if s.strip()]
            for sel in selectors:
                loc = self.page.locator(sel)
                count = await loc.count()
                if count > 0:
                    # pick first visible with href
                    for i in range(min(count, 10)):
                        candidate = loc.nth(i)
                        try:
                            href = await candidate.get_attribute("href")
                            is_visible = await candidate.is_visible()
                            if href and is_visible and not href.startswith("#"):
                                link = candidate
                                break
                        except Exception:
                            continue
                if link:
                    break

            # If no link found via selectors, try "Read more" text
            if not link and also_try_read_more:
                try:
                    loc = self.page.get_by_text("Read more")
                    if await loc.count() > 0:
                        link = loc.first
                except Exception:
                    pass

            if not link:
                return json.dumps(
                    {"status": "error", "error": "No post link found", "stage": "discover"},
                    indent=2,
                )

            async with self.page.expect_navigation():
                await link.click()

            # Wait a moment for dynamic content
            await self.page.wait_for_timeout(500)

            # Read content
            read_json = await self.read_page(include_html=read_include_html, max_chars=max_chars)
            try:
                data = json.loads(read_json)
            except Exception:
                return read_json

            data["status"] = "success"
            data["flow"] = "open_latest_post"
            return json.dumps(data, indent=2)
        except Exception as e:
            return json.dumps(
                {"status": "error", "error": str(e), "message": f"open_latest_post failed: {str(e)}"},
                indent=2,
            )
