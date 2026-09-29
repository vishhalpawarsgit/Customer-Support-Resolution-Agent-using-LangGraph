import os
from typing import Literal

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from .prompts import (
    UNDERSTAND_PROMPT,
    CLASSIFY_PROMPT,
    RESPONSE_PROMPT,
    REVIEW_PROMPT,
    FIX_PROMPT,
)
from .state import AgentState

load_dotenv()


class Classification(BaseModel):
    category: Literal[
        "ORDER_STATUS",
        "DAMAGED_PRODUCT",
        "WRONG_PRODUCT",
        "REFUND",
        "PAYMENT",
        "CANCELLATION",
        "OTHER",
    ] = Field(description="Support request category")
    priority: Literal["LOW", "MEDIUM", "HIGH"] = Field(description="Request priority")


class ReviewResult(BaseModel):
    approved: bool = Field(description="Whether the response is acceptable")
    feedback: str = Field(description="Actionable feedback; empty when approved")


def _llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")

    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    temperature = float(os.getenv("TEMPERATURE", "0"))
    return ChatGroq(
        model=model,
        temperature=temperature,
        api_key=api_key,
    )


def understand_node(state: AgentState) -> dict:
    llm = _llm()
    prompt = ChatPromptTemplate.from_template(UNDERSTAND_PROMPT)
    result = llm.invoke(prompt.format(customer_query=state["customer_query"]))
    return {"issue_summary": result.content.strip()}


def classify_node(state: AgentState) -> dict:
    llm = _llm().with_structured_output(Classification)
    prompt = ChatPromptTemplate.from_template(CLASSIFY_PROMPT)
    result = llm.invoke(
        prompt.format(
            customer_query=state["customer_query"],
            issue_summary=state["issue_summary"],
        )
    )
    return {"category": result.category, "priority": result.priority}


def response_node(state: AgentState) -> dict:
    llm = _llm()
    prompt = ChatPromptTemplate.from_template(RESPONSE_PROMPT)
    result = llm.invoke(
        prompt.format(
            customer_query=state["customer_query"],
            category=state["category"],
            priority=state["priority"],
            issue_summary=state["issue_summary"],
        )
    )
    return {"generated_response": result.content.strip()}


def review_node(state: AgentState) -> dict:
    llm = _llm().with_structured_output(ReviewResult)
    prompt = ChatPromptTemplate.from_template(REVIEW_PROMPT)
    result = llm.invoke(
        prompt.format(
            customer_query=state["customer_query"],
            category=state["category"],
            priority=state["priority"],
            issue_summary=state["issue_summary"],
            generated_response=state["generated_response"],
        )
    )
    return {"approved": result.approved, "review_feedback": result.feedback}


def fix_node(state: AgentState) -> dict:
    llm = _llm()
    prompt = ChatPromptTemplate.from_template(FIX_PROMPT)
    result = llm.invoke(
        prompt.format(
            customer_query=state["customer_query"],
            category=state["category"],
            priority=state["priority"],
            issue_summary=state["issue_summary"],
            generated_response=state["generated_response"],
            review_feedback=state["review_feedback"],
        )
    )
    return {
        "generated_response": result.content.strip(),
        "iteration_count": state["iteration_count"] + 1,
    }


def final_node(state: AgentState) -> dict:
    return {"final_response": state["generated_response"]}
