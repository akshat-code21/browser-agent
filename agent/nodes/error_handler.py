from ..state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from ..prompts.prompts import ERROR_SYSTEM, ERROR_USER
import json
from ...core.llm import model


def error_handler_node(state: AgentState):
    messages = [
        SystemMessage(ERROR_SYSTEM),
        HumanMessage(
            ERROR_USER.format(
                task=json.dumps(state.get("task", {}), ensure_ascii=False),
                action_history=json.dumps(
                    state.get("action_history", []), ensure_ascii=False
                ),
                error_message=json.dumps(
                    state.get("playwright_result", {}), ensure_ascii=False
                ),
                failed_action=json.dumps(state.get("analysis", {}), ensure_ascii=False),
                step_count=json.dumps(state.get("step_count", {}), ensure_ascii=False),
                max_steps="",
            )
        ),
    ]
    response = model.invoke(messages)
    state["error"] = str(response.content)
    return {**state, "error": response.content}
