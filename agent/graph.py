from langgraph.graph import StateGraph, START, END
from ..agent.state import AgentState
from ..agent.nodes.observe import observe_node
from ..agent.nodes.reason import reason_node
from ..agent.nodes.act import act_node
from ..agent.nodes.error_handler import error_handler_node
from ..agent.nodes.respond import response_node


def route_after_reason(state: AgentState):
    analysis = state.get("analysis", {})
    
    if analysis.get("is_complete"):
        return "response"

    if(analysis.get("action") == "scroll"):
        return "execute"

    return "execute"

def route_after_act(state:AgentState):
    result = state.get("playwright_result",{})
    status = result.get("status")

    if(status == "success"):
        analysis = state.get('analysis' , {})
        if analysis.get("is_complete"):
            return "respond"
        
        return "observe"
    
    return "error_handler"


agent = StateGraph(AgentState)
agent.add_node("observe_node", observe_node)
agent.add_node("reason_node", reason_node)
agent.add_node("act_node", act_node)
agent.add_node("error_handler_node", error_handler_node)
agent.add_node("response_node", response_node)

agent.set_entry_point("observe_node")

agent.add_conditional_edges("reason_node" , route_after_reason ,{"response" : "" , "execute" : ""})
