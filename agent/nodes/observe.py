from ..state import AgentState
from ...browser.observer import getScreenshot,getHtml

async def observe_node(state:AgentState):
    website_link = state.get("website_link")
    screenshot = await getScreenshot(website_link=website_link)
    html = await getHtml(website_link=website_link)
    
    state["screenshot"] = screenshot
    state["a11y_tree"] = html

    return {**state,"screenshot" : screenshot , "a11y_tree" : html}