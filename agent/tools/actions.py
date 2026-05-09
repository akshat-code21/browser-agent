from playwright.async_api import Page


async def click_event(page: Page, target: str):
    try:
        await page.get_by_role("button", name=target).click()
    except Exception:
        try:
            await page.get_by_role("link", name=target).click()
        except Exception:
            try:
                await page.get_by_text(target).first.click()
            except Exception as e:
                return {"status": "failure", "detail": str(e)}

    return {"status": "success", "detail": f"Clicked '{target}'"}


async def type_text(page: Page, target: str | None, value: str):
    try:
        await page.get_by_role("textbox", name=target).fill(value)
    except Exception:
        try:
            await page.get_by_role("searchbox", name=target).fill(value)
        except Exception as e:
            return {"status": "failure", "detail": str(e)}

    return {"status": "success", "detail": f"Typed '{value}' into '{target}'"}


async def scroll(page: Page, direction: str) -> dict:
    try:
        delta = 600 if direction == "down" else -600
        await page.mouse.wheel(0, delta)
        return {"status": "success", "detail": f"Scrolled {direction}"}
    except Exception as e:
        return {"status": "failure", "detail": str(e)}


async def extract(page: Page) -> dict:
    try:
        text = await page.inner_text("body")
        return {
            "status": "success",
            "detail": "Extracted page text",
            "extracted_text": text[:3000],
        }
    except Exception as e:
        return {"status": "failure", "detail": str(e)}


async def execute_action(page: Page, decision: dict):
    action = decision.get("action")
    target = decision.get("target")
    value = decision.get("value")
    direction = decision.get("scroll_direction", "down")

    if action == "click":
        return await click_event(page, str(target))

    elif action == "type":
        return await type_text(page, target, str(value))

    elif action == "scroll":
        return await scroll(page, direction)

    elif action == "extract":
        return await extract(page)

    elif action == "done":
        # no playwright call needed — reason.py already set is_complete + result
        return {"status": "success", "detail": "Task marked complete by agent"}

    else:
        return {
            "status": "failure",
            "detail": f"Unknown action '{action}' returned by reason node",
        }
