from typing import TypedDict


class AgentState(TypedDict):
    customer_query: str
    category: str
    priority: str
    issue_summary: str
    generated_response: str
    review_feedback: str
    approved: bool
    final_response: str
    iteration_count: int
