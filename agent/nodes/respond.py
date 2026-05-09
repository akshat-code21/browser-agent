from ..state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from ..prompts.prompts import RESPOND_SYSTEM, RESPOND_USER
import json
from ...core.llm import model


def response_node(state: AgentState):
    messages = [
        SystemMessage(RESPOND_SYSTEM),
        HumanMessage(
            RESPOND_USER.format(
                task=json.dumps(state.get("task", {}), ensure_ascii=False),
                is_complete=json.dumps(
                    state.get("is_complete", False), ensure_ascii=False
                ),
                result=json.dumps(state.get("analysis", {}).get("result"), ensure_ascii=False),
                action_history=json.dumps(
                    state.get("action_history", []), ensure_ascii=False
                ),
            )
        ),
    ]

    response = model.invoke(messages)
    print(response.to_json())
    return {**state, "final_response": response.content}
