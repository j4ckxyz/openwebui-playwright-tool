# Version Guide

## TL;DR: Use `playwright_async_tool.py` (v3.0.0)

---

## Version Comparison

| Version | File | Status | Works? | Reason |
|---------|------|--------|--------|--------|
| **v3.0.0** | `playwright_async_tool.py` | ✅ **RECOMMENDED** | ✅ Yes | Async API works in OpenWebUI's async context |
| v2.0.0 | `playwright_web_tool.py` | ❌ Broken | ❌ No | Sync API fails with "asyncio loop" error |
| v1.0.1 | `playwright_web_search_tool.py` | ⚠️ Deprecated | ❓ Maybe | Old async version, wrong package name |

---

## The Problem

OpenWebUI runs tools in an **async (asyncio) context**. When you use Playwright's synchronous API (`sync_playwright()`), you get this error:

```
Error: You are using the sync Playwright API in an asyncio loop. Use the async API instead.
```

## The Solution

Use **`playwright_async_tool.py`** which uses the async Playwright API (`async_playwright()`).

---

## Version History

### v3.0.0 (2024-10-19) ✅ CURRENT
**File:** `playwright_async_tool.py`

**What's New:**
- ✅ Uses `async_playwright()` and async/await throughout
- ✅ Works correctly in OpenWebUI's async environment
- ✅ Fixes "Sync API in asyncio loop" error
- ✅ Same 11 functions as v2.0.0
- ✅ Same return formats (JSON)
- ✅ Same detailed docstrings

**Installation:**
1. Copy `playwright_async_tool.py`
2. Paste in OpenWebUI Tools
3. Run: `docker exec -it open-webui playwright install chromium`

---

### v2.0.0 (2024-10-19) ❌ BROKEN
**File:** `playwright_web_tool.py`

**Why it exists:**
- Attempt to fix v1.0.1's package name issue
- Used synchronous API based on misunderstanding of OpenWebUI requirements

**Why it doesn't work:**
- ❌ OpenWebUI actually DOES run in async context
- ❌ Sync API causes runtime errors
- ❌ "You are using sync Playwright API in asyncio loop"

**Kept for:** Reference/learning purposes

---

### v1.0.1 (2024-10-19) ⚠️ DEPRECATED  
**File:** `playwright_web_search_tool.py`

**Problems:**
- ❌ Wrong package name: `playwright-python` (doesn't exist)
- ⚠️ Too many features (15+), overly complex
- ⚠️ Less clear documentation

**Why deprecated:**
- v3.0.0 is cleaner, simpler, and works correctly
- Fixed package requirement
- Better organized code

---

## Migration Guide

### From v2.0.0 to v3.0.0

**No changes needed!** The function signatures and return formats are identical. Just replace the file:

1. Delete old tool in OpenWebUI
2. Copy new `playwright_async_tool.py`
3. Paste and save
4. Done!

### From v1.0.1 to v3.0.0

Functions have been renamed/simplified:

| v1.0.1 | v3.0.0 |
|--------|--------|
| `get_page_content(content_type="text")` | `get_page_text()` |
| `get_page_content(content_type="html")` | `get_page_html()` |
| `set_cookie()` | ❌ Removed (rarely used) |
| `get_cookies()` | ❌ Removed (rarely used) |
| `get_network_requests()` | ❌ Removed (complex, rarely needed) |

All other functions remain the same!

---

## Which Features Are in v3.0.0?

✅ **11 Core Functions:**

1. `navigate_to_url()` - Go to URLs
2. `get_page_text()` - Extract visible text
3. `get_page_html()` - Get HTML source
4. `click_element()` - Click elements
5. `fill_input()` - Fill forms
6. `extract_elements()` - Scrape data
7. `take_screenshot()` - Capture images
8. `execute_javascript()` - Run custom JS
9. `wait_for_element()` - Wait for dynamic content
10. `search_google()` - Quick Google search
11. `close_browser()` - Clean up

---

## FAQ

### Q: Why so many versions in one day?
**A:** We encountered the package name issue (v1.0.1), tried to fix it with sync API (v2.0.0), then realized OpenWebUI needs async API (v3.0.0). Third time's the charm! 🎯

### Q: Should I use sync or async?
**A:** **Always use async** (`playwright_async_tool.py`). OpenWebUI runs tools in an async context.

### Q: What if I already installed v2.0.0?
**A:** Replace it with v3.0.0. The API is identical, it just works now! 😄

### Q: Will there be a v4.0.0?
**A:** Hopefully not needed! v3.0.0 should be stable. Any future updates will likely be minor (v3.1.0, etc.)

### Q: Can I use the sync version outside OpenWebUI?
**A:** Yes! If you're writing a standalone Python script (not for OpenWebUI), `playwright_web_tool.py` works fine. But for OpenWebUI, use the async version.

---

## Summary

| If you want... | Use this file |
|----------------|---------------|
| **To use in OpenWebUI** | `playwright_async_tool.py` v3.0.0 ✅ |
| A standalone Python script | `playwright_web_tool.py` v2.0.0 |
| To understand what went wrong | Read this document 😊 |

---

**Bottom line:** Download and use [`playwright_async_tool.py`](./playwright_async_tool.py). That's it! 🚀
