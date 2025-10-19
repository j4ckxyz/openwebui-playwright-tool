# Quick Start Guide

## Step 1: Copy the Tool Code

1. Open [`playwright_async_tool.py`](./playwright_async_tool.py)
2. Copy all the code (Ctrl+A, Ctrl+C)

## Step 2: Add to OpenWebUI

1. In OpenWebUI, click **Workspace** in the sidebar
2. Click **Tools** tab
3. Click **+ Create Tool** button
4. Paste the code
5. Click **Save**
6. Wait for "Tool saved successfully" message

## Step 3: Install Browser (REQUIRED)

The Playwright package will install automatically, but you **must** install browser binaries:

### For Docker Users:
```bash
docker exec -it open-webui playwright install chromium
```

### For Non-Docker:
```bash
playwright install chromium
```

### If you get errors about missing libraries:
```bash
docker exec -u root -it open-webui playwright install-deps chromium
```

## Step 4: Test It Out

1. Start a new chat in OpenWebUI
2. Click the **+** icon at the bottom
3. Enable the **Playwright Web Automation** tool
4. Try these test prompts:

### Test 1: Simple Navigation
```
Navigate to https://example.com and tell me what you see
```

### Test 2: Google Search
```
Search Google for "OpenWebUI features" and summarize the top 3 results
```

### Test 3: Screenshot
```
Go to https://openwebui.com and take a screenshot
```

### Test 4: Data Extraction
```
Navigate to https://news.ycombinator.com and extract the titles and URLs of the top 5 posts
```

## Troubleshooting

### "Executable doesn't exist" error
- You forgot Step 3! Run: `docker exec -it open-webui playwright install chromium`

### "Tool not appearing in chat"
- Make sure you saved the tool successfully
- Refresh your browser page
- Check Admin Settings → Tools to verify it's there

### "Timeout" errors
- Some websites are slow. Try increasing the timeout in tool settings (gear icon)
- Or use `wait_until="domcontentloaded"` for faster loading

### Still having issues?
- Check [INSTALLATION.md](./INSTALLATION.md) for detailed troubleshooting
- Open an issue on [GitHub](https://github.com/j4ckxyz/openwebui-playwright-tool/issues)

## What Can You Do With It?

✅ **Search the web** and get real-time information  
✅ **Extract data** from websites (prices, news, listings, etc.)  
✅ **Take screenshots** for visual analysis  
✅ **Fill forms** and interact with web apps  
✅ **Monitor content** changes over time  
✅ **Scrape data** for research and analysis  

## Next Steps

- Read [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for all available commands
- Check [README.md](./README.md) for detailed feature descriptions
- Explore the tool's Valves (settings) for customization

## Pro Tips

💡 **Always close the browser** when done: Just say "close the browser"  
💡 **Use specific selectors**: `#id` and `.class` work better than generic `div`  
💡 **Wait for dynamic content**: Use `wait_for_element()` before extracting  
💡 **Test selectors first**: Use browser DevTools to verify CSS selectors  

Enjoy web automation! 🚀
