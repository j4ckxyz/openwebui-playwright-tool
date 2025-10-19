# OpenWebUI Playwright Tool (Single-File)

One Python tool, one README. Copy `playwright_async_tool.py` into OpenWebUI and you’re ready to automate the web: navigate, click, extract, screenshot.

## Quick Start

- File: `playwright_async_tool.py` (async, recommended)
- Requires: `playwright` Python package + browser binaries

Steps
1) In OpenWebUI: Workspace → Tools → + Create Tool → paste the contents of `playwright_async_tool.py` → Save
2) Install browser once (Docker or local):
   - Docker: `docker exec -it open-webui playwright install chromium`
   - Local: `playwright install chromium`
3) In chat: click + and enable the tool

Headless-only: The tool always launches headless for reliability across servers, containers, and CI. No headed mode is exposed.

## What You Get

- navigate_to_url(url, wait_until)
- get_page_text(), get_page_html()
- click_element(selector, wait_for_navigation)
- fill_input(selector, value, submit)
- extract_elements(selector, attributes="text,href", max_elements)
- take_screenshot(full_page=False, element_selector=None)
- execute_javascript(script)
- wait_for_element(selector, state="visible", timeout)
- search_google(query, num_results)
- scroll_page(direction)
- close_browser()
- click_by_text(text, exact=False, wait_for_navigation=True)
- accept_cookies()
- read_page(main_selectors=..., include_html=False)
- open_latest_post(base_url, post_link_selectors=..., also_try_read_more=True)

All functions return JSON (or strings for page content), suitable for tool output.

## Minimal Examples

Navigate
```python
await navigate_to_url(url="https://example.com", wait_until="load")
```

Extract links
```python
await extract_elements(selector="a", attributes="text,href", max_elements=5)
```

Fill + submit
```python
await fill_input(selector="#q", value="playwright", submit=True)
```

Screenshot
```python
await take_screenshot(full_page=True)
```

Wait for UI
```python
await wait_for_element(selector=".results", state="visible", timeout=10000)
```

## Valves (Config)

- BROWSER_TYPE: `chromium` | `firefox` | `webkit` (default `chromium`)
- DEFAULT_TIMEOUT: ms (default `30000`)
- VIEWPORT_WIDTH / VIEWPORT_HEIGHT: ints (default `1280`/`720`)

## Troubleshooting

- Missing browser binary
  - Docker: `docker exec -it open-webui playwright install chromium`
  - Local: `playwright install chromium` (and `playwright install-deps chromium` on Linux if needed)

- X server errors (Missing DISPLAY)
  - Not applicable: the tool is headless-only. If a GUI is absolutely required in CI, wrap commands with `xvfb-run`, but the tool itself remains headless.

- Timeouts / dynamic pages
  - Use `wait_until="domcontentloaded"` or `"networkidle"`
  - Call `wait_for_element(...)` before interacting

- Cleanup
  - Always call `close_browser()` when done to free resources

## Notes

- This repo intentionally ships with one script and one README for simplicity.
- License: MIT (see LICENSE)
- Credits: Playwright, OpenWebUI
