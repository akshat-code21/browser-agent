import asyncio
from typing import Optional
from pyppeteer import launch
import base64
from openrouter import OpenRouter
import os
from dotenv import load_dotenv
load_dotenv()

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
    websiteLink: str, x: Optional[int] = None, y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None
):
    browser = await launch(options={"headless": False})
    page = await browser.newPage()
    await page.goto(websiteLink, wait_until="load")

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
    return html


async def getScreenshot(
    websiteLink: str,
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
):
    browser = await launch(options={"headless": False})
    page = await browser.newPage()
    await page.goto(websiteLink, wait_until="load")

    if x is not None and y is not None and width is not None and height is not None:
        clip = {"x": x, "y": y, "width": width, "height": height}
        screenshot_bytes = await page.screenshot(type="png", clip=clip)
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


async def get_response(screenshot, html):
    max_html_length = 3000
    truncated_html = html[:max_html_length] + (
        "..." if len(html) > max_html_length else ""
    )

    with OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY")) as client:
        response = client.chat.send(
            model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are a specialist in understanding websites. Analyze the provided screenshot and HTML to determine what the website is about.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{screenshot}"},
                        },
                        {
                            "type": "text",
                            "text": f"HTML content (truncated):\n{truncated_html}\n\nWhat is this website about?",
                        },
                    ],
                },
            ],
        )
    return response


async def main(website: str = "https://www.scaler.com"):
    screenshot = await getScreenshot(website)
    html = await getHtml(website, x=0, y=0, width=500, height=500)
    result = await get_response(screenshot=screenshot, html=html)
    print(result.choices[0].message.content)


if __name__ == "__main__":
    import sys

    website = sys.argv[1] if len(sys.argv) > 1 else "https://www.scaler.com"

    asyncio.run(main(website=website))
