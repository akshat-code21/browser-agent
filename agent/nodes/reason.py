from ..state import AgentState
from ...core.llm import model
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Any
import json
from ..prompts.prompts import REASON_SYSTEM, REASON_USER


async def reason_node(state: AgentState):
    screenshot = state.get("screenshot")
    html = state.get("a11y_tree")

    messages = [
        SystemMessage(REASON_SYSTEM),
        HumanMessage(
            content=[
                REASON_USER.format(
                    task=json.dumps(state.get("task", {}), ensure_ascii=False),
                    url=json.dumps(state.get("website_link", ""), ensure_ascii=False),
                    a11y_tree=html,
                    action_history=state.get("action_history"),
                ),
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{screenshot}"},
                },
            ]
        ),
    ]

    response = model.invoke(messages)
    analysis = parse_json_object(response.content)
    if analysis is None:
        return {**state, "error": "model returned invalid file analysis JSON"}

    state["analysis"] = analysis
    return {**state, "analysis": analysis}


def parse_json_list(content: Any) -> list[dict[str, Any]] | None:
    text = _response_text(content)
    if not text:
        return None

    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None

    # if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
    #     return None
    
    return value


def _response_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "".join(parts).strip()
    return ""


def parse_json_object(content: Any) -> dict[str, Any] | None:
    text = _response_text(content)
    if not text:
        return None
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    return value

