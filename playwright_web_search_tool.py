"""
title: Playwright Web Search & Automation Tool
author: OpenWebUI Community
author_url: https://github.com/open-webui/open-webui
git_url: https://github.com/open-webui/open-webui
description: A comprehensive Playwright-based web automation tool that enables models to search the web, interact with pages, extract content, take screenshots, and perform advanced browser automation tasks.
required_open_webui_version: 0.4.0
requirements: playwright
version: 1.0.0
licence: MIT
"""

import asyncio
import base64
import json
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any, Union
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeoutError


class Tools:
    class Valves(BaseModel):
        BROWSER_TYPE: str = Field(
            default="chromium",
            description="Browser to use: chromium, firefox, or webkit"
        )
        HEADLESS: bool = Field(
            default=True,
            description="Run browser in headless mode (no visible window)"
        )
        DEFAULT_TIMEOUT: int = Field(
            default=30000,
            description="Default timeout for operations in milliseconds"
        )
        DEFAULT_NAVIGATION_TIMEOUT: int = Field(
            default=30000,
            description="Default navigation timeout in milliseconds"
        )
        VIEWPORT_WIDTH: int = Field(
            default=1280,
            description="Browser viewport width in pixels"
        )
        VIEWPORT_HEIGHT: int = Field(
            default=720,
            description="Browser viewport height in pixels"
        )
        USER_AGENT: str = Field(
            default="",
            description="Custom user agent string (leave empty for default)"
        )
        ENABLE_JAVASCRIPT: bool = Field(
            default=True,
            description="Enable JavaScript execution"
        )
        MAX_SCREENSHOTS: int = Field(
            default=5,
            description="Maximum number of screenshots to keep in memory"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._screenshot_cache = []

    async def _ensure_browser(self):
        """Ensures browser, context, and page are initialized."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        if not self.browser:
            browser_type = getattr(self.playwright, self.valves.BROWSER_TYPE)
            self.browser = await browser_type.launch(headless=self.valves.HEADLESS)
        
        if not self.context:
            context_options = {
                "viewport": {
                    "width": self.valves.VIEWPORT_WIDTH,
                    "height": self.valves.VIEWPORT_HEIGHT
                },
                "java_script_enabled": self.valves.ENABLE_JAVASCRIPT
            }
            if self.valves.USER_AGENT:
                context_options["user_agent"] = self.valves.USER_AGENT
            
            self.context = await self.browser.new_context(**context_options)
            self.context.set_default_timeout(self.valves.DEFAULT_TIMEOUT)
            self.context.set_default_navigation_timeout(self.valves.DEFAULT_NAVIGATION_TIMEOUT)
        
        if not self.page:
            self.page = await self.context.new_page()

    async def navigate_to_url(
        self,
        url: str = Field(..., description="The URL to navigate to (must include protocol like https://)"),
        wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = Field(
            default="load",
            description="When to consider navigation succeeded: 'load' (full page load), 'domcontentloaded' (DOM ready), 'networkidle' (no network activity), 'commit' (initial response received)"
        )
    ) -> str:
        """
        Navigate to a specified URL and wait for the page to load.
        
        Returns: JSON with navigation status, final URL, and page title.
        Output format: {"status": "success", "url": "https://...", "title": "Page Title", "message": "Navigated successfully"}
        """
        try:
            await self._ensure_browser()
            response = await self.page.goto(url, wait_until=wait_until)
            
            title = await self.page.title()
            final_url = self.page.url
            
            return json.dumps({
                "status": "success",
                "url": final_url,
                "title": title,
                "status_code": response.status if response else None,
                "message": f"Successfully navigated to {final_url}"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to navigate to {url}: {str(e)}"
            })

    async def get_page_content(
        self,
        content_type: Literal["html", "text", "title", "url"] = Field(
            default="text",
            description="Type of content to retrieve: 'html' (full HTML), 'text' (visible text), 'title' (page title), 'url' (current URL)"
        )
    ) -> str:
        """
        Extract content from the current page.
        
        Returns: The requested content as a string or JSON object.
        Output format: For 'html'/'text'/'title'/'url': direct string. Contains the page content.
        """
        try:
            await self._ensure_browser()
            
            if content_type == "html":
                content = await self.page.content()
            elif content_type == "text":
                content = await self.page.evaluate("() => document.body.innerText")
            elif content_type == "title":
                content = await self.page.title()
            elif content_type == "url":
                content = self.page.url
            
            return content
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to get page content: {str(e)}"
            })

    async def click_element(
        self,
        selector: str = Field(..., description="CSS selector, text selector, or role selector for the element to click (e.g., 'button#submit', 'text=Click me', 'role=button[name=\"Submit\"]')"),
        wait_for_navigation: bool = Field(
            default=False,
            description="Wait for navigation after clicking (useful for links and form submits)"
        ),
        timeout: int = Field(
            default=30000,
            description="Timeout in milliseconds for the click operation"
        )
    ) -> str:
        """
        Click an element on the current page using a selector.
        
        Returns: JSON with click result and any navigation info.
        Output format: {"status": "success", "message": "Clicked element", "navigated": true/false, "new_url": "..."}
        """
        try:
            await self._ensure_browser()
            
            if wait_for_navigation:
                async with self.page.expect_navigation():
                    await self.page.click(selector, timeout=timeout)
                navigated = True
                new_url = self.page.url
            else:
                await self.page.click(selector, timeout=timeout)
                navigated = False
                new_url = None
            
            return json.dumps({
                "status": "success",
                "message": f"Successfully clicked element: {selector}",
                "navigated": navigated,
                "new_url": new_url
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to click element {selector}: {str(e)}"
            })

    async def fill_input(
        self,
        selector: str = Field(..., description="CSS selector for the input field (e.g., 'input[name=\"email\"]', '#search-box')"),
        value: str = Field(..., description="Text value to enter into the input field"),
        submit: bool = Field(
            default=False,
            description="Press Enter after filling (useful for search boxes)"
        )
    ) -> str:
        """
        Fill an input field with text. Works with text inputs, textareas, and contenteditable elements.
        
        Returns: JSON with fill operation status.
        Output format: {"status": "success", "message": "Filled input field", "submitted": true/false}
        """
        try:
            await self._ensure_browser()
            
            await self.page.fill(selector, value)
            
            if submit:
                await self.page.press(selector, "Enter")
            
            return json.dumps({
                "status": "success",
                "message": f"Successfully filled input {selector} with value",
                "submitted": submit
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to fill input {selector}: {str(e)}"
            })

    async def extract_elements(
        self,
        selector: str = Field(..., description="CSS selector to find elements (e.g., 'a.product-link', 'div.search-result')"),
        attributes: List[str] = Field(
            default=["text"],
            description="Attributes to extract from each element: 'text' (inner text), 'html' (inner HTML), 'href', 'src', 'class', or any HTML attribute"
        ),
        max_elements: int = Field(
            default=10,
            description="Maximum number of elements to extract (to prevent overwhelming output)"
        )
    ) -> str:
        """
        Extract data from multiple elements matching a selector. Useful for scraping lists, links, or structured data.
        
        Returns: JSON array of extracted element data.
        Output format: [{"text": "...", "href": "...", ...}, {...}] - Array of objects with requested attributes.
        """
        try:
            await self._ensure_browser()
            
            elements = await self.page.query_selector_all(selector)
            results = []
            
            for element in elements[:max_elements]:
                element_data = {}
                for attr in attributes:
                    if attr == "text":
                        element_data["text"] = await element.inner_text()
                    elif attr == "html":
                        element_data["html"] = await element.inner_html()
                    else:
                        element_data[attr] = await element.get_attribute(attr)
                results.append(element_data)
            
            return json.dumps({
                "status": "success",
                "count": len(results),
                "elements": results,
                "message": f"Extracted {len(results)} elements"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to extract elements: {str(e)}"
            })

    async def take_screenshot(
        self,
        full_page: bool = Field(
            default=False,
            description="Capture the entire scrollable page (true) or just the visible viewport (false)"
        ),
        element_selector: Optional[str] = Field(
            default=None,
            description="Optional CSS selector to screenshot only a specific element instead of the full page"
        )
    ) -> str:
        """
        Take a screenshot of the current page or a specific element. Returns base64-encoded PNG image.
        
        Returns: JSON with base64-encoded screenshot data.
        Output format: {"status": "success", "image": "data:image/png;base64,...", "dimensions": {"width": 1280, "height": 720}}
        """
        try:
            await self._ensure_browser()
            
            screenshot_options = {"type": "png"}
            
            if element_selector:
                element = await self.page.query_selector(element_selector)
                if not element:
                    return json.dumps({
                        "status": "error",
                        "message": f"Element not found: {element_selector}"
                    })
                screenshot_bytes = await element.screenshot(**screenshot_options)
            else:
                screenshot_options["full_page"] = full_page
                screenshot_bytes = await self.page.screenshot(**screenshot_options)
            
            base64_image = base64.b64encode(screenshot_bytes).decode('utf-8')
            data_uri = f"data:image/png;base64,{base64_image}"
            
            if len(self._screenshot_cache) >= self.valves.MAX_SCREENSHOTS:
                self._screenshot_cache.pop(0)
            self._screenshot_cache.append(data_uri)
            
            return json.dumps({
                "status": "success",
                "image": data_uri,
                "timestamp": datetime.now().isoformat(),
                "message": "Screenshot captured successfully"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to take screenshot: {str(e)}"
            })

    async def execute_javascript(
        self,
        script: str = Field(..., description="JavaScript code to execute in the page context"),
        return_result: bool = Field(
            default=True,
            description="Return the result of the JavaScript expression (false for side-effect only scripts)"
        )
    ) -> str:
        """
        Execute custom JavaScript code in the page context. Useful for complex DOM manipulation or data extraction.
        
        Returns: JSON with script execution result or confirmation.
        Output format: {"status": "success", "result": <evaluated value>, "type": "<type of result>"}
        """
        try:
            await self._ensure_browser()
            
            if return_result:
                result = await self.page.evaluate(script)
                result_type = type(result).__name__
            else:
                await self.page.evaluate(script)
                result = None
                result_type = "None"
            
            return json.dumps({
                "status": "success",
                "result": result,
                "result_type": result_type,
                "message": "JavaScript executed successfully"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to execute JavaScript: {str(e)}"
            })

    async def wait_for_element(
        self,
        selector: str = Field(..., description="CSS selector for the element to wait for"),
        state: Literal["attached", "detached", "visible", "hidden"] = Field(
            default="visible",
            description="Element state to wait for: 'attached' (in DOM), 'detached' (removed from DOM), 'visible' (displayed), 'hidden' (not displayed)"
        ),
        timeout: int = Field(
            default=30000,
            description="Timeout in milliseconds to wait for the element"
        )
    ) -> str:
        """
        Wait for an element to reach a specific state. Essential for handling dynamic content and SPAs.
        
        Returns: JSON with wait result.
        Output format: {"status": "success", "message": "Element reached desired state", "state": "visible"}
        """
        try:
            await self._ensure_browser()
            
            await self.page.wait_for_selector(selector, state=state, timeout=timeout)
            
            return json.dumps({
                "status": "success",
                "message": f"Element {selector} reached state: {state}",
                "state": state
            })
        except PlaywrightTimeoutError:
            return json.dumps({
                "status": "error",
                "error": "Timeout",
                "message": f"Element {selector} did not reach state {state} within {timeout}ms"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to wait for element: {str(e)}"
            })

    async def scroll_page(
        self,
        direction: Literal["up", "down", "top", "bottom"] = Field(
            default="down",
            description="Scroll direction: 'up' (one page up), 'down' (one page down), 'top' (scroll to top), 'bottom' (scroll to bottom)"
        ),
        amount: Optional[int] = Field(
            default=None,
            description="Scroll amount in pixels (overrides direction presets)"
        )
    ) -> str:
        """
        Scroll the page in various directions. Useful for loading dynamic content or navigating long pages.
        
        Returns: JSON with scroll operation status.
        Output format: {"status": "success", "message": "Scrolled page", "direction": "down"}
        """
        try:
            await self._ensure_browser()
            
            if amount is not None:
                script = f"window.scrollBy(0, {amount})"
            elif direction == "top":
                script = "window.scrollTo(0, 0)"
            elif direction == "bottom":
                script = "window.scrollTo(0, document.body.scrollHeight)"
            elif direction == "up":
                script = "window.scrollBy(0, -window.innerHeight)"
            elif direction == "down":
                script = "window.scrollBy(0, window.innerHeight)"
            
            await self.page.evaluate(script)
            
            return json.dumps({
                "status": "success",
                "message": f"Page scrolled {direction}",
                "direction": direction
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to scroll page: {str(e)}"
            })

    async def get_cookies(self) -> str:
        """
        Retrieve all cookies for the current domain.
        
        Returns: JSON array of cookie objects.
        Output format: [{"name": "cookie_name", "value": "...", "domain": "...", "path": "/", ...}, ...]
        """
        try:
            await self._ensure_browser()
            
            cookies = await self.context.cookies()
            
            return json.dumps({
                "status": "success",
                "count": len(cookies),
                "cookies": cookies,
                "message": f"Retrieved {len(cookies)} cookies"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to get cookies: {str(e)}"
            })

    async def set_cookie(
        self,
        name: str = Field(..., description="Cookie name"),
        value: str = Field(..., description="Cookie value"),
        domain: Optional[str] = Field(default=None, description="Cookie domain (defaults to current page domain)"),
        path: str = Field(default="/", description="Cookie path"),
        expires: Optional[int] = Field(default=None, description="Cookie expiration timestamp (Unix time in seconds)")
    ) -> str:
        """
        Set a cookie in the browser context. Useful for authentication or session management.
        
        Returns: JSON with operation status.
        Output format: {"status": "success", "message": "Cookie set successfully"}
        """
        try:
            await self._ensure_browser()
            
            cookie = {
                "name": name,
                "value": value,
                "path": path
            }
            
            if domain:
                cookie["domain"] = domain
            else:
                current_url = self.page.url
                from urllib.parse import urlparse
                cookie["domain"] = urlparse(current_url).netloc
            
            if expires:
                cookie["expires"] = expires
            
            await self.context.add_cookies([cookie])
            
            return json.dumps({
                "status": "success",
                "message": f"Cookie '{name}' set successfully"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to set cookie: {str(e)}"
            })

    async def search_google(
        self,
        query: str = Field(..., description="Search query to execute on Google"),
        num_results: int = Field(default=5, description="Number of search results to extract (1-20)")
    ) -> str:
        """
        Perform a Google search and extract the top results. A high-level convenience function for web searching.
        
        Returns: JSON with search results including titles, URLs, and snippets.
        Output format: {"status": "success", "query": "...", "results": [{"title": "...", "url": "...", "snippet": "..."}, ...]}
        """
        try:
            await self._ensure_browser()
            
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            await self.page.goto(search_url, wait_until="networkidle")
            
            await asyncio.sleep(1)
            
            results = []
            search_results = await self.page.query_selector_all("div.g")
            
            for result in search_results[:num_results]:
                try:
                    title_elem = await result.query_selector("h3")
                    link_elem = await result.query_selector("a")
                    snippet_elem = await result.query_selector("div.VwiC3b")
                    
                    if title_elem and link_elem:
                        title = await title_elem.inner_text()
                        url = await link_elem.get_attribute("href")
                        snippet = await snippet_elem.inner_text() if snippet_elem else ""
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
                except:
                    continue
            
            return json.dumps({
                "status": "success",
                "query": query,
                "count": len(results),
                "results": results,
                "message": f"Found {len(results)} search results"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to perform Google search: {str(e)}"
            })

    async def close_browser(self) -> str:
        """
        Close the browser and clean up resources. Use this when you're done with web automation.
        
        Returns: JSON with closure status.
        Output format: {"status": "success", "message": "Browser closed successfully"}
        """
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
            
            self._screenshot_cache.clear()
            
            return json.dumps({
                "status": "success",
                "message": "Browser closed and resources cleaned up successfully"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to close browser cleanly: {str(e)}"
            })

    async def get_network_requests(
        self,
        url_pattern: Optional[str] = Field(
            default=None,
            description="Optional URL pattern to filter requests (e.g., '*.json', '*api*')"
        )
    ) -> str:
        """
        Capture network requests made by the page. Useful for debugging or monitoring API calls.
        Note: This requires setting up request interception before navigating.
        
        Returns: JSON with captured network requests.
        Output format: {"status": "success", "requests": [{"url": "...", "method": "GET", "status": 200}, ...]}
        """
        try:
            await self._ensure_browser()
            
            requests = []
            
            async def handle_request(request):
                if url_pattern is None or url_pattern in request.url:
                    requests.append({
                        "url": request.url,
                        "method": request.method,
                        "headers": request.headers
                    })
            
            async def handle_response(response):
                if url_pattern is None or url_pattern in response.url:
                    for req in requests:
                        if req["url"] == response.url:
                            req["status"] = response.status
                            req["status_text"] = response.status_text
                            break
            
            self.page.on("request", handle_request)
            self.page.on("response", handle_response)
            
            return json.dumps({
                "status": "success",
                "message": "Network monitoring enabled. Requests will be captured on subsequent page loads.",
                "note": "This is a setup function. Navigate to a page to capture its requests."
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to set up network monitoring: {str(e)}"
            })
