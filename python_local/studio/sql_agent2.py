"""SQL agent for studio."""

import pathlib
import re

import requests
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool

llm = init_chat_model("openai:gpt-5")

# database is from:
# url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"

db = SQLDatabase.from_uri("sqlite:///Chinook.db")

@tool
def execute_sql(query: str) -> str:
    """Execute a query and return results."""

    try:
        return db.run(query)
    except Exception as e:
        return f"Error: {e}"


SYSTEM_PROMPT = """You are a careful SQLite analyst.

Rules:
- Think step-by-step.
- When you need data, call the tool `execute_sql` with ONE SELECT query.
- Read-only only; no INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/REPLACE/TRUNCATE.
- Limit to 5 rows of output unless the user explicitly asks otherwise.
- If the tool returns 'Error:', revise the SQL and try again.
- Prefer explicit column lists; avoid SELECT *.
"""
# currently, studio lacks support for passing in runtime context

agent = create_agent(
    model=llm,
    tools=[execute_sql],
    system_prompt=SYSTEM_PROMPT,
)

# Example:
# question = "Which genre on average has the longest tracks?"
# for step in agent.stream({"messages": [{"role":"user","content": question}]}, stream_mode="values"):
#    step["messages"][-1].pretty_print()
