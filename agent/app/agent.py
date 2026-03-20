"""LangGraph ReAct agent setup for configuration management."""

import os
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from .tools import all_tools

SYSTEM_PROMPT = """You are a configuration management assistant for a microservices platform.
You help users manage application configurations stored in the database.

RULES:
- ALWAYS search for a config before creating it to avoid duplicates
- If a config already exists when user asks to add it, inform them with the current value and ask if they want to update
- Valid environments are: dev, staging, prod
- If the user doesn't specify an environment, ask them which one
- If the user doesn't specify a service name, ask them which service
- When listing configs, format them in a readable way
- Be concise and helpful
- After creating/updating/deleting, confirm what was done

AVAILABLE SERVICES (for reference): auth-service, payment-service, order-service
But users can create configs for any service name.
"""


def create_agent():
    """Create and return the ReAct agent. Raises if Ollama is unavailable."""
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
    )
    return create_react_agent(llm, all_tools, prompt=SYSTEM_PROMPT)
