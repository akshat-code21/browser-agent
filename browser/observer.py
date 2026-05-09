from typing import Optional
from playwright.async_api import async_playwright
import asyncio
import base64

async def getScreenshot(
    website_link: str,
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(website_link, wait_until="load")

        if x is not None and y is not None and width is not None and height is not None:
            cx, cy, cw, ch = x, y, width, height
            screenshot_bytes = await page.screenshot(
                type="png",
                clip={
                    "x": float(cx),
                    "y": float(cy),
                    "width": float(cw),
                    "height": float(ch),
                },
            )
        else:
            await _prepare_page_for_full_screenshot(page)
            screenshot_bytes = await page.screenshot(type="png", full_page=True)

        if isinstance(screenshot_bytes, str):
            screenshot_bytes = screenshot_bytes.encode("utf-8")
        base64_image = base64.b64encode(screenshot_bytes).decode("utf-8")
        await browser.close()
        with open("screenshot.png", "wb") as f:
            f.write(base64.b64decode(base64_image))
        print("Screenshot saved as screenshot.png")
    return base64_image
async def _prepare_page_for_full_screenshot(page) -> None:
    """Wait for quieter network and scroll so lazy-loaded content appears before capture."""
    try:
        await page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception:
        pass

    await page.evaluate(
        """async () => {
            const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
            const step = Math.max(200, Math.floor(window.innerHeight * 0.75));
            const maxY = Math.max(
                document.documentElement.scrollHeight,
                document.body?.scrollHeight ?? 0,
            );
            for (let y = 0; y < maxY; y += step) {
                window.scrollTo(0, y);
                await sleep(50);
            }
            window.scrollTo(0, maxY);
            await sleep(150);
            window.scrollTo(0, 0);
            await sleep(100);
        }"""
    )
    await asyncio.sleep(0.3)

async def getHtml(
    website_link: str, x: Optional[int] = None, y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None
):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(website_link, wait_until="load")

        if x is not None and y is not None and width is not None and height is not None:
            html = await page.evaluate(f"""
                () => {{
                    const element = document.elementFromPoint({x}, {y});
                    if (!element) return null;
                    // Try to get the closest parent that's reasonably sized
                    let target = element;
                    while (target && target !== document.body) {{
                        const rect = target.getBoundingClientRect();
                        if (rect.height > 50 && rect.width > 50) break;
                        target = target.parentElement;
                    }}
                    return target ? target.outerHTML : null;
                }}
            """)
        else:
            html = await page.content()

    await browser.close()
    print(html)
    return html