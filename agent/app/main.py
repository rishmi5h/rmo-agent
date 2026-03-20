"""FastAPI app exposing the /agent/chat endpoint."""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from .agent import create_agent
from .session_store import store

load_dotenv()

agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the agent on startup."""
    global agent
    try:
        agent = create_agent()
    except Exception as e:
        print(f"Warning: Failed to create agent: {e}")
    yield


app = FastAPI(
    title="Config Agent",
    description="LangGraph-based configuration management agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ToolCallInfo(BaseModel):
    tool: str
    input: dict


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[ToolCallInfo] | None = None


@app.post("/agent/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message to the agent and get a response with tool call transparency."""
    if agent is None:
        return ChatResponse(
            reply="LLM not available — make sure Ollama is running with the configured model "
                  f"({os.getenv('OLLAMA_MODEL', 'llama3.1:8b')}). "
                  "Start it with: `ollama run llama3.1:8b`",
            tool_calls=None,
        )

    # Build message history for this session
    history = store.get_messages(request.session_id)
    input_messages = history + [HumanMessage(content=request.message)]

    try:
        # Invoke the agent
        result = await agent.ainvoke({"messages": input_messages})
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            return ChatResponse(
                reply="LLM not available — make sure Ollama is running with the configured model. "
                      "Start it with: `ollama run llama3.1:8b`",
                tool_calls=None,
            )
        return ChatResponse(reply=f"Agent error: {error_msg}", tool_calls=None)

    # Extract the final AI reply and any tool calls from intermediate steps
    output_messages = result["messages"]
    tool_calls_info: list[ToolCallInfo] = []
    reply_text = ""

    for msg in output_messages:
        # Collect tool call info from AI messages for transparency
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls_info.append(ToolCallInfo(tool=tc["name"], input=tc["args"]))
        # The last AI message (without tool calls) is the final reply
        if isinstance(msg, AIMessage) and not msg.tool_calls and msg.content:
            reply_text = msg.content

    # Store the conversation turn
    store.add_messages(request.session_id, [
        HumanMessage(content=request.message),
        AIMessage(content=reply_text),
    ])

    return ChatResponse(
        reply=reply_text or "I wasn't able to generate a response. Please try again.",
        tool_calls=tool_calls_info if tool_calls_info else None,
    )


@app.get("/agent/health")
async def health_check():
    """Health check — reports whether the agent/LLM is available."""
    return {"status": "ok", "agent_ready": agent is not None}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AGENT_PORT", "8001"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
