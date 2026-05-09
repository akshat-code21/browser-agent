from langgraph.graph import StateGraph, END
from ..agent.state import AgentState
from ..agent.nodes.observe import observe_node
from ..agent.nodes.reason import reason_node
from ..agent.nodes.act import act_node
from ..agent.nodes.error_handler import error_handler_node
from ..agent.nodes.respond import response_node
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
import uuid


def route_after_act(state: AgentState):
    result = state.get("playwright_result", {})
    status = result.get("status")

    if status == "success":
        analysis = state.get("analysis", {})
        if analysis.get("is_complete"):
            return "respond"

        return "observe"

    return "error_handler"


builder = StateGraph(AgentState)
builder.add_node("observe_node", observe_node)
builder.add_node("reason_node", reason_node)
builder.add_node("act_node", act_node)
builder.add_node("error_handler_node", error_handler_node)
builder.add_node("response_node", response_node)

builder.set_entry_point("observe_node")

builder.add_edge("observe_node", "reason_node")
builder.add_edge("reason_node", "act_node")

builder.add_conditional_edges(
    "act_node",
    route_after_act,
    {
        "respond": "response_node",
        "observe": "observe_node",
        "error_handler": "error_handler_node",
    },
)

builder.add_edge("response_node", END)
builder.add_edge("error_handler_node", END)


checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)


async def run_agent(website_link: str, task: str):
    config: RunnableConfig = {
        "configurable": {
            "website_link": website_link,
            "thread_id": f"${uuid.uuid4().hex[:8]}",
        }
    }
    state: AgentState = {"website_link": website_link, "task": task}

    result = graph.invoke(state, config=config)
    
    print(result)
    
    return result
