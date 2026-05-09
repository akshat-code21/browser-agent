from openrouter.errors import OpenRouterError, ResponseValidationError
from openrouter import OpenRouter
import json
import os
from langchain_openrouter import ChatOpenRouter


model = ChatOpenRouter(
    model="openai/gpt-oss-120b:free",
    temperature=0,
    max_retries=2
)

def _raise_openrouter_failure(exc: OpenRouterError) -> None:
    """OpenRouter sometimes returns HTTP 200 with {\"error\": ...} (e.g. provider timeout 524)."""
    if isinstance(exc, ResponseValidationError):
        raw = exc.body or ""
        try:
            payload = json.loads(raw)
            err = payload.get("error")
            if isinstance(err, dict):
                code = err.get("code", "?")
                msg = err.get("message", raw[:500])
                raise RuntimeError(
                    f"OpenRouter error in response body (HTTP {exc.raw_response.status_code}, "
                    f"code {code}): {msg}. "
                    "Often code 524 means the upstream model timed out—retry, use a smaller screenshot, "
                    "or switch model."
                ) from exc
        except json.JSONDecodeError:
            pass
        raise RuntimeError(
            f"OpenRouter response did not match the expected chat schema "
            f"(HTTP {exc.raw_response.status_code}). First 500 chars of body: {raw[:500]!r}"
        ) from exc
    raise RuntimeError(
        f"OpenRouter request failed (HTTP {exc.status_code}): {exc.message}"
    ) from exc


async def get_response(screenshot, html):
    max_html_length = 3000
    truncated_html = html

    try:
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
    except (ResponseValidationError, OpenRouterError) as e:
        _raise_openrouter_failure(e)
    return response
