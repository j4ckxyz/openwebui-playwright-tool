# Installation Guide

## Quick Start

### 1. Add Tool to OpenWebUI

1. Copy the contents of [`playwright_web_search_tool.py`](./playwright_web_search_tool.py)
2. In OpenWebUI, go to **Workspace** → **Tools**
3. Click **"+ Create Tool"**
4. Paste the code
5. Click **Save**
6. Wait for the success message (Playwright package will auto-install)

### 2. Install Browser Binaries (REQUIRED)

After saving the tool, you **must** install browser binaries or the tool will not work.

#### For Docker Installations

```bash
# Install Chromium browser
docker exec -it open-webui playwright install chromium

# Install system dependencies (if you get errors)
docker exec -u root -it open-webui playwright install-deps chromium
```

#### For Non-Docker Installations

```bash
# Install Chromium browser
playwright install chromium

# Install system dependencies (Linux only, if needed)
playwright install-deps chromium
```

### 3. Test the Tool

In OpenWebUI chat, enable the Playwright tool and try:

```
Navigate to https://example.com and tell me what you see
```

or

```
Search Google for "OpenWebUI features" and summarize the results
```

## Detailed Installation for Docker

### Standard Docker Setup

```bash
# 1. Access your container
docker exec -it open-webui bash

# 2. Install browser
playwright install chromium

# 3. Exit container
exit
```

### Docker with System Dependencies

If you encounter errors like "missing shared libraries", install system deps:

```bash
# Run as root to install packages
docker exec -u root -it open-webui bash

# Install dependencies
apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

# Install browser as regular user
su - abc  # or the user running OpenWebUI
playwright install chromium
exit
```

### Dockerfile Modification (Optional)

For a permanent solution, add to your Dockerfile:

```dockerfile
# Install Playwright and browsers
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps chromium
```

## Troubleshooting Installation

### Error: "Executable doesn't exist at /ms-playwright/chromium-*/chrome-linux/chrome"

**Solution:** Browser binaries aren't installed.

```bash
docker exec -it open-webui playwright install chromium
```

### Error: "error while loading shared libraries: libnss3.so"

**Solution:** Missing system dependencies.

```bash
docker exec -u root -it open-webui playwright install-deps chromium
```

### Error: "Could not find browser"

**Solution:** Wrong browser type configured.

1. In OpenWebUI, go to **Workspace** → **Tools**
2. Click on the Playwright tool
3. Click the gear icon (⚙️) to configure Valves
4. Ensure `BROWSER_TYPE` is set to `chromium` (or whichever you installed)

### Error: "Permission denied"

**Solution:** Container user doesn't have write permissions.

```bash
# Run as root
docker exec -u root -it open-webui playwright install chromium

# Or give permissions to the user directory
docker exec -u root -it open-webui chown -R abc:abc /home/abc/.cache
```

### Tool saves but doesn't work

**Checklist:**
- ✅ Playwright package installed? (automatic on save)
- ✅ Browser binaries installed? (`playwright install chromium`)
- ✅ System dependencies installed? (`playwright install-deps chromium`)
- ✅ Tool enabled in chat? (click the + icon and enable it)
- ✅ Correct valve settings? (check BROWSER_TYPE matches installed browser)

## Verifying Installation

### Check Playwright Installation

```bash
docker exec -it open-webui pip show playwright
```

Should show:
```
Name: playwright
Version: 1.40.0 (or higher)
```

### Check Browser Installation

```bash
docker exec -it open-webui playwright --version
```

Should show:
```
Version 1.40.0
```

### List Installed Browsers

```bash
docker exec -it open-webui ls -la ~/.cache/ms-playwright/
```

Should show directories like:
```
chromium-<version>/
firefox-<version>/  (if installed)
webkit-<version>/   (if installed)
```

## Storage Requirements

| Browser | Disk Space |
|---------|------------|
| Chromium | ~150 MB |
| Firefox | ~180 MB |
| WebKit | ~100 MB |
| All three | ~450 MB |

**Recommendation:** Install only Chromium unless you specifically need other browsers.

## Docker Compose Example

```yaml
version: '3'
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    volumes:
      - open-webui:/app/backend/data
    ports:
      - "3000:8080"
    environment:
      - WEBUI_AUTH=False
    # Install Playwright browsers on container start
    command: >
      sh -c "
        playwright install chromium &&
        playwright install-deps chromium &&
        /app/backend/start.sh
      "

volumes:
  open-webui:
```

## Alternative: Manual Python Installation

If you're not using Docker:

```bash
# Install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium

# Install system dependencies (Linux)
sudo playwright install-deps chromium
```

## Getting Help

If you're still having issues:

1. Check the [main README](./README.md) for usage examples
2. Review the [troubleshooting section](./README.md#troubleshooting)
3. Open an issue on [GitHub](https://github.com/j4ckxyz/openwebui-playwright-tool/issues)

Include this information:
- OpenWebUI version
- Installation method (Docker/non-Docker)
- OS/platform
- Error messages
- Output of `playwright --version`
