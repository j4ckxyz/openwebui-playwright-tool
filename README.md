# Playwright Web Search & Automation Tool for OpenWebUI

A comprehensive Playwright-based web automation tool that enables AI models in OpenWebUI to search the web, interact with pages, extract content, take screenshots, and perform advanced browser automation tasks.

## Features

### 🌐 Navigation & Page Control
- **navigate_to_url()** - Navigate to any URL with configurable wait conditions (load, domcontentloaded, networkidle, commit)
- **get_page_content()** - Extract HTML, text, title, or current URL from the page
- **scroll_page()** - Scroll in any direction (up, down, top, bottom) or by specific pixel amounts

### 🖱️ Element Interaction
- **click_element()** - Click elements using CSS selectors, text selectors, or ARIA role selectors
- **fill_input()** - Fill form fields and inputs with optional auto-submit
- **wait_for_element()** - Wait for elements to appear/disappear/become visible/hidden

### 📊 Data Extraction
- **extract_elements()** - Scrape multiple elements with customizable attributes (text, href, src, any HTML attribute)
- **execute_javascript()** - Run custom JavaScript code for complex DOM manipulation or data extraction
- **get_cookies()** / **set_cookie()** - Manage browser cookies for authentication and session handling

### 📸 Visual Capture
- **take_screenshot()** - Capture full page, viewport, or specific elements as base64-encoded PNG images
- Returns data URI format for easy embedding and display

### 🔍 High-Level Automation
- **search_google()** - Convenience function for Google searches with automatic result extraction
- **get_network_requests()** - Monitor and capture network traffic patterns
- **close_browser()** - Clean up resources and close browser sessions

## Installation

### Prerequisites
1. OpenWebUI version 0.4.0 or higher
2. Python 3.11+

### Install Dependencies

The tool will automatically install required packages when loaded in OpenWebUI, but you can also install them manually:

```bash
pip install playwright playwright-python
playwright install chromium  # or firefox/webkit
```

### Add to OpenWebUI

1. Copy the contents of `playwright_web_search_tool.py`
2. In OpenWebUI, navigate to **Workspace → Tools**
3. Click **"+ Create Tool"**
4. Paste the code
5. Click **Save**

## Configuration (Valves)

The tool provides several configuration options via Valves:

| Valve | Default | Description |
|-------|---------|-------------|
| **BROWSER_TYPE** | `chromium` | Browser engine to use: `chromium`, `firefox`, or `webkit` |
| **HEADLESS** | `true` | Run browser in headless mode (no visible window) |
| **DEFAULT_TIMEOUT** | `30000` | Default timeout for operations in milliseconds |
| **DEFAULT_NAVIGATION_TIMEOUT** | `30000` | Navigation timeout in milliseconds |
| **VIEWPORT_WIDTH** | `1280` | Browser viewport width in pixels |
| **VIEWPORT_HEIGHT** | `720` | Browser viewport height in pixels |
| **USER_AGENT** | `""` | Custom user agent string (empty = browser default) |
| **ENABLE_JAVASCRIPT** | `true` | Enable/disable JavaScript execution |
| **MAX_SCREENSHOTS** | `5` | Maximum number of screenshots to cache in memory |

## Usage Examples

### Basic Web Search
```python
# Perform a Google search
await search_google(
    query="latest AI developments 2024",
    num_results=5
)
```

### Navigate and Extract Data
```python
# Navigate to a page
await navigate_to_url(
    url="https://example.com/articles",
    wait_until="networkidle"
)

# Extract article information
await extract_elements(
    selector="article.post",
    attributes=["text", "href", "data-id"],
    max_elements=10
)
```

### Form Interaction
```python
# Fill a search form
await fill_input(
    selector="#search-input",
    value="playwright automation",
    submit=True
)

# Click a button
await click_element(
    selector="button[type='submit']",
    wait_for_navigation=True
)
```

### Visual Analysis
```python
# Take a full-page screenshot
await take_screenshot(full_page=True)

# Screenshot a specific element
await take_screenshot(
    element_selector="#chart-container"
)
```

### Advanced JavaScript Execution
```python
# Execute custom JavaScript
await execute_javascript(
    script="""
        return Array.from(document.querySelectorAll('a'))
            .map(a => ({ text: a.textContent, href: a.href }))
            .slice(0, 10);
    """,
    return_result=True
)
```

### Cookie Management
```python
# Set authentication cookie
await set_cookie(
    name="session_token",
    value="abc123...",
    domain=".example.com",
    path="/",
    expires=1735689600
)

# Retrieve all cookies
await get_cookies()
```

### Dynamic Content Handling
```python
# Wait for dynamic content to load
await wait_for_element(
    selector="div.results-loaded",
    state="visible",
    timeout=10000
)

# Scroll to load more content
await scroll_page(direction="bottom")
```

## Output Format

All tools return structured JSON responses:

### Success Response
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": { /* tool-specific data */ }
}
```

### Error Response
```json
{
  "status": "error",
  "error": "Error type or message",
  "message": "Detailed error description"
}
```

### Example Screenshot Response
```json
{
  "status": "success",
  "image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "timestamp": "2024-10-19T14:30:45.123456",
  "message": "Screenshot captured successfully"
}
```

## Best Practices

### Resource Management
Always close the browser when done to free up resources:
```python
await close_browser()
```

### Timeout Handling
For slow-loading pages, increase timeouts:
```python
await navigate_to_url(
    url="https://slow-site.com",
    wait_until="networkidle"  # Waits for network to be idle
)
```

### Selector Best Practices
Use specific selectors to avoid ambiguity:
- ✅ `"button#submit"` - ID selector (most specific)
- ✅ `"role=button[name='Submit']"` - ARIA role selector
- ✅ `"text=Click Here"` - Text content selector
- ⚠️ `"button"` - Too generic, matches first button

### Error Handling
The tool returns structured errors. Always check the `status` field:
```javascript
const result = JSON.parse(await navigate_to_url(...));
if (result.status === "error") {
    console.error(result.message);
}
```

## Troubleshooting

### Browser Not Launching
```bash
# Install browsers manually
playwright install chromium
playwright install firefox
playwright install webkit
```

### Timeout Errors
- Increase `DEFAULT_TIMEOUT` in Valves
- Use `wait_until="domcontentloaded"` instead of `"load"` for faster navigation
- Check if the target website is accessible

### Element Not Found
- Use `wait_for_element()` before interacting with dynamic content
- Verify selectors in browser DevTools
- Try different selector strategies (CSS, text, role)

### Memory Issues
- Reduce `MAX_SCREENSHOTS` in Valves
- Call `close_browser()` regularly to free resources
- Use `element_selector` for screenshots instead of `full_page`

## Security Considerations

⚠️ **Important Security Notes:**

1. **User Input Validation**: This tool executes arbitrary JavaScript and navigates to user-provided URLs. Ensure proper input validation.
2. **Sandboxing**: Run in isolated environments when possible
3. **Cookie Security**: Cookies are stored in memory and cleared on browser close
4. **Screenshot Privacy**: Screenshots may contain sensitive information
5. **Rate Limiting**: Implement rate limits to prevent abuse

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Credits

Built with:
- [Playwright](https://playwright.dev/) - Browser automation framework
- [OpenWebUI](https://github.com/open-webui/open-webui) - AI interface platform

## Changelog

### v1.0.0 (2024-10-19)
- Initial release
- Support for Chromium, Firefox, and WebKit browsers
- 15+ automation tools covering navigation, interaction, extraction, and capture
- Configurable valves for customization
- Comprehensive error handling and JSON output format
