from ..state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from ...core.llm import model
from ..prompts.prompts import ACT_SYSTEM, ACT_USER
import json


def act_node(state: AgentState):
    messages = [
        SystemMessage(ACT_SYSTEM),
        HumanMessage(
            content=[
                ACT_USER.format(
                    task=json.dumps(state.get("task", {}), ensure_ascii=False),
                    attempted_action=json.dumps(
                        state.get("analysis", {}), ensure_ascii=False
                    ),
                    playwright_result=json.dumps(
                        state.get("playwright_result", {}), ensure_ascii=False
                    ),
                ),
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{state.get('screenshot')}"
                    },
                },
            ]
        ),
    ]

    response = model.invoke(messages)
    action_res = json.loads(str(response.content))

    if action_res is None:
        return {**state, "error": "model couldn't provide an action"}

    return {**state, "playwright_result": action_res}
