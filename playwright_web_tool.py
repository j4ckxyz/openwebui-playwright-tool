"""
title: Playwright Web Automation
author: j4ckxyz
author_url: https://github.com/j4ckxyz
git_url: https://github.com/j4ckxyz/openwebui-playwright-tool
description: Comprehensive browser automation tool enabling AI models to navigate websites, interact with elements, extract data, and capture screenshots using Playwright.
required_open_webui_version: 0.4.0
requirements: playwright
version: 2.0.0
licence: MIT
"""

import json
import base64
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeoutError


class Tools:
    class Valves(BaseModel):
        BROWSER_TYPE: str = Field(
            default="chromium",
            description="Browser engine: chromium, firefox, or webkit"
        )
        HEADLESS: bool = Field(
            default=True,
            description="Run browser without visible window"
        )
        DEFAULT_TIMEOUT: int = Field(
            default=30000,
            description="Operation timeout in milliseconds"
        )
        VIEWPORT_WIDTH: int = Field(
            default=1280,
            description="Browser viewport width"
        )
        VIEWPORT_HEIGHT: int = Field(
            default=720,
            description="Browser viewport height"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def _ensure_browser(self):
        """Initialize browser if not already running"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
        
        if not self.browser:
            browser_type = getattr(self.playwright, self.valves.BROWSER_TYPE)
            self.browser = browser_type.launch(headless=self.valves.HEADLESS)
        
        if not self.context:
            self.context = self.browser.new_context(
                viewport={
                    "width": self.valves.VIEWPORT_WIDTH,
                    "height": self.valves.VIEWPORT_HEIGHT
                }
            )
            self.context.set_default_timeout(self.valves.DEFAULT_TIMEOUT)
        
        if not self.page:
            self.page = self.context.new_page()

    def navigate_to_url(
        self,
        url: str = Field(..., description="Full URL to navigate to (must include https:// or http://)"),
        wait_until: Literal["load", "domcontentloaded", "networkidle"] = Field(
            default="load",
            description="When navigation is considered complete: 'load' (full page), 'domcontentloaded' (DOM ready), 'networkidle' (no network activity)"
        )
    ) -> str:
        """
        Navigate to a URL and wait for page to load.
        
        Returns JSON with:
        - status: "success" or "error"
        - url: final URL after navigation (may differ due to redirects)
        - title: page title
        - message: human-readable result description
        
        Example: navigate_to_url(url="https://example.com", wait_until="load")
        """
        try:
            self._ensure_browser()
            response = self.page.goto(url, wait_until=wait_until)
            
            return json.dumps({
                "status": "success",
                "url": self.page.url,
                "title": self.page.title(),
                "status_code": response.status if response else None,
                "message": f"Navigated to {self.page.url}"
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Navigation failed: {str(e)}"
            }, indent=2)

    def get_page_text(self) -> str:
        """
        Extract all visible text from the current page.
        
        Returns: Plain text content of the page body.
        Use this to understand what's on the page before extracting specific elements.
        
        Example: get_page_text()
        """
        try:
            self._ensure_browser()
            text = self.page.evaluate("() => document.body.innerText")
            return text
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            }, indent=2)

    def get_page_html(self) -> str:
        """
        Get the full HTML source of the current page.
        
        Returns: Complete HTML source code.
        Useful for detailed analysis or when you need to see the page structure.
        
        Example: get_page_html()
        """
        try:
            self._ensure_browser()
            return self.page.content()
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            }, indent=2)

    def click_element(
        self,
        selector: str = Field(..., description="CSS selector for the element to click (e.g., 'button#submit', '.menu-item', 'a[href=\"/login\"]')"),
        wait_for_navigation: bool = Field(
            default=False,
            description="Wait for page navigation after clicking (useful for links and form submissions)"
        )
    ) -> str:
        """
        Click an element on the page using a CSS selector.
        
        Returns JSON with:
        - status: "success" or "error"
        - message: description of what happened
        - navigated: whether page navigation occurred
        - new_url: URL after navigation (if navigated)
        
        Selector types you can use:
        - ID: "button#submit"
        - Class: ".nav-link"
        - Attribute: "input[name='email']"
        - Text: "text=Click Here"
        
        Example: click_element(selector="button.login-btn", wait_for_navigation=True)
        """
        try:
            self._ensure_browser()
            
            if wait_for_navigation:
                with self.page.expect_navigation():
                    self.page.click(selector)
                return json.dumps({
                    "status": "success",
                    "message": f"Clicked {selector} and navigated",
                    "navigated": True,
                    "new_url": self.page.url
                }, indent=2)
            else:
                self.page.click(selector)
                return json.dumps({
                    "status": "success",
                    "message": f"Clicked {selector}",
                    "navigated": False
                }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to click {selector}: {str(e)}"
            }, indent=2)

    def fill_input(
        self,
        selector: str = Field(..., description="CSS selector for the input field (e.g., 'input#email', 'textarea[name=\"message\"]')"),
        value: str = Field(..., description="Text to enter into the field"),
        submit: bool = Field(
            default=False,
            description="Press Enter after filling (useful for search boxes)"
        )
    ) -> str:
        """
        Fill a text input, textarea, or contenteditable element with text.
        
        Returns JSON with:
        - status: "success" or "error"
        - message: description of action taken
        - submitted: whether Enter was pressed
        
        This clears the field first, then types the new value.
        
        Example: fill_input(selector="#search-box", value="playwright tutorial", submit=True)
        """
        try:
            self._ensure_browser()
            
            self.page.fill(selector, value)
            
            if submit:
                self.page.press(selector, "Enter")
            
            return json.dumps({
                "status": "success",
                "message": f"Filled {selector} with text",
                "submitted": submit
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to fill {selector}: {str(e)}"
            }, indent=2)

    def extract_elements(
        self,
        selector: str = Field(..., description="CSS selector to find multiple elements (e.g., 'a.product-link', 'div.search-result')"),
        attributes: str = Field(
            default="text,href",
            description="Comma-separated attributes to extract: 'text' (visible text), 'html' (inner HTML), 'href', 'src', 'class', or any HTML attribute"
        ),
        max_elements: int = Field(
            default=10,
            description="Maximum number of matching elements to extract (1-100)"
        )
    ) -> str:
        """
        Extract data from multiple elements matching a selector.
        
        Returns JSON array of objects, each containing the requested attributes.
        
        Common attributes:
        - text: visible text content
        - html: inner HTML
        - href: link URL
        - src: image/script source
        - class: CSS classes
        - data-*: custom data attributes
        
        Example: extract_elements(selector="article.post", attributes="text,href,data-id", max_elements=5)
        Returns: [{"text": "Post Title", "href": "/post/1", "data-id": "123"}, ...]
        """
        try:
            self._ensure_browser()
            
            attr_list = [a.strip() for a in attributes.split(",")]
            elements = self.page.query_selector_all(selector)
            results = []
            
            for element in elements[:max_elements]:
                element_data = {}
                for attr in attr_list:
                    if attr == "text":
                        element_data["text"] = element.inner_text()
                    elif attr == "html":
                        element_data["html"] = element.inner_html()
                    else:
                        element_data[attr] = element.get_attribute(attr)
                results.append(element_data)
            
            return json.dumps({
                "status": "success",
                "count": len(results),
                "elements": results
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Failed to extract elements: {str(e)}"
            }, indent=2)

    def take_screenshot(
        self,
        full_page: bool = Field(
            default=False,
            description="Capture entire scrollable page (true) or just visible viewport (false)"
        ),
        element_selector: Optional[str] = Field(
            default=None,
            description="Optional: CSS selector to screenshot only a specific element"
        )
    ) -> str:
        """
        Capture a screenshot as a base64-encoded PNG image.
        
        Returns JSON with:
        - status: "success" or "error"
        - image: data URI (data:image/png;base64,...)
        - timestamp: when screenshot was taken
        
        The image data URI can be displayed directly in markdown or HTML.
        
        Examples:
        - Full page: take_screenshot(full_page=True)
        - Viewport only: take_screenshot(full_page=False)
        - Specific element: take_screenshot(element_selector="#chart-container")
        """
        try:
            self._ensure_browser()
            
            if element_selector:
                element = self.page.query_selector(element_selector)
                if not element:
                    return json.dumps({
                        "status": "error",
                        "message": f"Element not found: {element_selector}"
                    }, indent=2)
                screenshot_bytes = element.screenshot(type="png")
            else:
                screenshot_bytes = self.page.screenshot(type="png", full_page=full_page)
            
            base64_image = base64.b64encode(screenshot_bytes).decode('utf-8')
            data_uri = f"data:image/png;base64,{base64_image}"
            
            return json.dumps({
                "status": "success",
                "image": data_uri,
                "timestamp": datetime.now().isoformat(),
                "message": "Screenshot captured"
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Screenshot failed: {str(e)}"
            }, indent=2)

    def execute_javascript(
        self,
        script: str = Field(..., description="JavaScript code to execute in the page context")
    ) -> str:
        """
        Execute custom JavaScript code and return the result.
        
        Returns JSON with:
        - status: "success" or "error"
        - result: the evaluated JavaScript expression result
        - result_type: Python type of the result
        
        The script is executed in the page context and has access to the DOM.
        
        Examples:
        - Get element count: execute_javascript(script="return document.querySelectorAll('a').length")
        - Get page data: execute_javascript(script="return {title: document.title, url: location.href}")
        - Manipulate DOM: execute_javascript(script="document.body.style.background = 'red'; return 'changed'")
        """
        try:
            self._ensure_browser()
            
            result = self.page.evaluate(script)
            
            return json.dumps({
                "status": "success",
                "result": result,
                "result_type": type(result).__name__
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"JavaScript execution failed: {str(e)}"
            }, indent=2)

    def wait_for_element(
        self,
        selector: str = Field(..., description="CSS selector for the element to wait for"),
        state: Literal["attached", "detached", "visible", "hidden"] = Field(
            default="visible",
            description="Element state to wait for: 'attached' (in DOM), 'detached' (removed), 'visible' (displayed), 'hidden' (not displayed)"
        ),
        timeout: int = Field(
            default=30000,
            description="Maximum time to wait in milliseconds"
        )
    ) -> str:
        """
        Wait for an element to reach a specific state.
        
        Returns JSON with:
        - status: "success" or "error"
        - message: what happened
        - state: the state that was reached
        
        States:
        - attached: element exists in DOM
        - detached: element removed from DOM
        - visible: element is displayed (not display:none or visibility:hidden)
        - hidden: element is not visible
        
        Essential for dynamic content, AJAX requests, and single-page applications.
        
        Example: wait_for_element(selector=".results-loaded", state="visible", timeout=10000)
        """
        try:
            self._ensure_browser()
            
            self.page.wait_for_selector(selector, state=state, timeout=timeout)
            
            return json.dumps({
                "status": "success",
                "message": f"Element {selector} reached state: {state}",
                "state": state
            }, indent=2)
        except PlaywrightTimeoutError:
            return json.dumps({
                "status": "error",
                "error": "Timeout",
                "message": f"Element {selector} did not reach state {state} within {timeout}ms"
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Wait failed: {str(e)}"
            }, indent=2)

    def search_google(
        self,
        query: str = Field(..., description="Search query text"),
        num_results: int = Field(
            default=5,
            description="Number of search results to extract (1-20)"
        )
    ) -> str:
        """
        Perform a Google search and extract results.
        
        Returns JSON with:
        - status: "success" or "error"
        - query: the search query used
        - count: number of results found
        - results: array of {title, url, snippet} objects
        
        This is a high-level convenience function that navigates to Google,
        submits the search, and extracts the top results.
        
        Example: search_google(query="OpenWebUI features", num_results=5)
        Returns: {"status": "success", "results": [{"title": "...", "url": "...", "snippet": "..."}, ...]}
        """
        try:
            self._ensure_browser()
            
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            self.page.goto(search_url, wait_until="networkidle")
            
            self.page.wait_for_timeout(1000)
            
            results = []
            search_results = self.page.query_selector_all("div.g")
            
            for result in search_results[:num_results]:
                try:
                    title_elem = result.query_selector("h3")
                    link_elem = result.query_selector("a")
                    snippet_elem = result.query_selector("div.VwiC3b")
                    
                    if title_elem and link_elem:
                        results.append({
                            "title": title_elem.inner_text(),
                            "url": link_elem.get_attribute("href"),
                            "snippet": snippet_elem.inner_text() if snippet_elem else ""
                        })
                except:
                    continue
            
            return json.dumps({
                "status": "success",
                "query": query,
                "count": len(results),
                "results": results
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Google search failed: {str(e)}"
            }, indent=2)

    def scroll_page(
        self,
        direction: Literal["up", "down", "top", "bottom"] = Field(
            default="down",
            description="Scroll direction: 'up' (one page), 'down' (one page), 'top' (beginning), 'bottom' (end)"
        )
    ) -> str:
        """
        Scroll the page in the specified direction.
        
        Returns JSON with:
        - status: "success" or "error"
        - message: description of scroll action
        - direction: the direction scrolled
        
        Useful for:
        - Loading dynamic content that appears on scroll
        - Navigating long pages
        - Triggering infinite scroll mechanisms
        
        Example: scroll_page(direction="bottom")
        """
        try:
            self._ensure_browser()
            
            if direction == "top":
                script = "window.scrollTo(0, 0)"
            elif direction == "bottom":
                script = "window.scrollTo(0, document.body.scrollHeight)"
            elif direction == "up":
                script = "window.scrollBy(0, -window.innerHeight)"
            elif direction == "down":
                script = "window.scrollBy(0, window.innerHeight)"
            
            self.page.evaluate(script)
            
            return json.dumps({
                "status": "success",
                "message": f"Scrolled {direction}",
                "direction": direction
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Scroll failed: {str(e)}"
            }, indent=2)

    def close_browser(self) -> str:
        """
        Close the browser and clean up all resources.
        
        Returns JSON with:
        - status: "success" or "error"
        - message: confirmation of cleanup
        
        Call this when you're done with browser automation to free up memory.
        A new browser will be started automatically if you call other tools after closing.
        
        Example: close_browser()
        """
        try:
            if self.page:
                self.page.close()
                self.page = None
            if self.context:
                self.context.close()
                self.context = None
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            
            return json.dumps({
                "status": "success",
                "message": "Browser closed and resources cleaned up"
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Cleanup failed: {str(e)}"
            }, indent=2)
