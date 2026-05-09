from typing_extensions import TypedDict, NotRequired, Required
from typing import Literal


class StepLog(TypedDict):
    step: int
    action: Literal["click", "type", "scroll", "extract", "done"]
    target: str
    outcome: str

class AgentState(TypedDict, total=False):
    website_link: Required[str]
    task: Required[str]
    screenshot: str
    a11y_tree: str
    step_count: int
    action_history: list[StepLog]
    playwright_result:dict
    is_complete: bool
    analysis: dict
    error: NotRequired[str]
    final_response: str  

