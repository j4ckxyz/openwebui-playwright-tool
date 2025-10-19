# Quick Reference Card

## Installation (One-Time Setup)

```bash
# 1. Add tool in OpenWebUI (Workspace → Tools → + Create Tool)
# 2. Install browser in Docker container:
docker exec -it open-webui playwright install chromium
```

## Common Commands

### Navigation
```python
# Go to a URL
navigate_to_url(url="https://example.com", wait_until="load")

# Get page content
get_page_content(content_type="text")  # or "html", "title", "url"
```

### Search
```python
# Quick Google search
search_google(query="OpenWebUI features", num_results=5)
```

### Interaction
```python
# Click an element
click_element(selector="button#submit", wait_for_navigation=False)

# Fill a form field
fill_input(selector="#search", value="playwright", submit=True)

# Wait for element
wait_for_element(selector="div.results", state="visible", timeout=30000)
```

### Data Extraction
```python
# Extract multiple elements
extract_elements(
    selector="a.product-link",
    attributes=["text", "href", "data-price"],
    max_elements=10
)

# Custom JavaScript
execute_javascript(
    script="return document.querySelectorAll('h1')[0].textContent",
    return_result=True
)
```

### Screenshots
```python
# Full page screenshot
take_screenshot(full_page=True)

# Specific element
take_screenshot(element_selector="#chart")
```

### Cookies
```python
# Get all cookies
get_cookies()

# Set a cookie
set_cookie(
    name="session",
    value="abc123",
    domain=".example.com"
)
```

### Page Control
```python
# Scroll
scroll_page(direction="bottom")  # "up", "down", "top", "bottom"

# Close browser
close_browser()
```

## Selector Types

### CSS Selectors
- `"button#submit"` - ID
- `".product-card"` - Class
- `"input[name='email']"` - Attribute
- `"div > p"` - Direct child

### Text Selectors
- `"text=Click Here"` - Exact text
- `"text=/submit/i"` - Regex (case-insensitive)

### Role Selectors (Recommended)
- `"role=button[name='Submit']"` - ARIA role + name
- `"role=link[name='Learn More']"` - Link by text

## Wait States

- `"load"` - Wait for full page load (default)
- `"domcontentloaded"` - DOM ready, faster
- `"networkidle"` - No network activity for 500ms
- `"commit"` - Initial response received

## Common Patterns

### Search and Extract Results
```python
# Navigate to search page
navigate_to_url("https://example.com/search")

# Fill search form
fill_input(selector="#search-input", value="query", submit=True)

# Wait for results
wait_for_element(selector=".search-results", state="visible")

# Extract results
extract_elements(
    selector=".result-item",
    attributes=["text", "href"],
    max_elements=10
)
```

### Login Flow
```python
# Navigate to login page
navigate_to_url("https://example.com/login")

# Fill credentials
fill_input(selector="#username", value="user@example.com")
fill_input(selector="#password", value="secret")

# Submit
click_element(selector="button[type='submit']", wait_for_navigation=True)

# Verify login
get_cookies()  # Check for session cookie
```

### Infinite Scroll
```python
# Navigate to page
navigate_to_url("https://example.com/feed")

# Scroll multiple times to load content
for i in range(5):
    scroll_page(direction="down")
    wait_for_element(selector=f".item[data-index='{i * 10}']", state="visible")

# Extract all loaded items
extract_elements(selector=".item", attributes=["text", "href"], max_elements=50)
```

## Troubleshooting Quick Fixes

### Element Not Found
```python
# Add explicit wait before interaction
wait_for_element(selector="button#submit", state="visible", timeout=10000)
click_element(selector="button#submit")
```

### Stale Element
```python
# Re-query the element instead of reusing
extract_elements(selector=".dynamic-content", attributes=["text"])
```

### Timeout
```python
# Increase timeout or use faster wait condition
navigate_to_url(url="https://slow-site.com", wait_until="domcontentloaded")
```

## Configuration (Valves)

Access via: **Workspace → Tools → Playwright Tool → ⚙️ Settings**

| Setting | Default | Options |
|---------|---------|---------|
| BROWSER_TYPE | chromium | chromium, firefox, webkit |
| HEADLESS | true | true, false |
| DEFAULT_TIMEOUT | 30000 | milliseconds |
| VIEWPORT_WIDTH | 1280 | pixels |
| VIEWPORT_HEIGHT | 720 | pixels |

## Return Format

All functions return JSON:

```json
{
  "status": "success",  // or "error"
  "message": "Operation completed",
  "data": { /* tool-specific data */ }
}
```

## Common Errors

| Error | Solution |
|-------|----------|
| `Executable doesn't exist` | Run `playwright install chromium` |
| `Timeout exceeded` | Increase timeout or change wait condition |
| `Element not found` | Check selector, wait for element first |
| `Navigation timeout` | Use `wait_until="domcontentloaded"` |

## Best Practices

✅ **DO:**
- Use specific selectors (ID > class > tag)
- Wait for elements before interacting
- Use `role` selectors for accessibility
- Close browser when done
- Check `status` in returned JSON

❌ **DON'T:**
- Use generic selectors like `"div"` or `"span"`
- Interact without waiting for element
- Keep browser open unnecessarily
- Ignore error responses

## Need More Help?

- Full docs: [README.md](./README.md)
- Installation: [INSTALLATION.md](./INSTALLATION.md)
- Issues: [GitHub Issues](https://github.com/j4ckxyz/openwebui-playwright-tool/issues)
