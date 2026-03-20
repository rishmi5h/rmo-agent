"""In-memory session history manager for agent conversations."""

import time
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

MAX_MESSAGES_PER_SESSION = 50
SESSION_TTL_SECONDS = 3600  # 1 hour


class SessionStore:
    """Stores per-session conversation history with automatic cleanup."""

    def __init__(self):
        # session_id -> {"messages": [...], "last_access": timestamp}
        self._sessions: dict[str, dict] = {}

    def get_messages(self, session_id: str) -> list[BaseMessage]:
        """Get conversation history for a session."""
        self._cleanup_stale_sessions()
        session = self._sessions.get(session_id)
        if not session:
            return []
        session["last_access"] = time.time()
        return session["messages"]

    def add_messages(self, session_id: str, messages: list[BaseMessage]):
        """Append messages to a session, trimming if over the limit."""
        if session_id not in self._sessions:
            self._sessions[session_id] = {"messages": [], "last_access": time.time()}

        session = self._sessions[session_id]
        session["messages"].extend(messages)
        session["last_access"] = time.time()

        # Trim oldest messages if over limit
        if len(session["messages"]) > MAX_MESSAGES_PER_SESSION:
            session["messages"] = session["messages"][-MAX_MESSAGES_PER_SESSION:]

    def clear_session(self, session_id: str):
        """Remove a session entirely."""
        self._sessions.pop(session_id, None)

    def _cleanup_stale_sessions(self):
        """Remove sessions that haven't been accessed within the TTL."""
        now = time.time()
        stale = [
            sid for sid, data in self._sessions.items()
            if now - data["last_access"] > SESSION_TTL_SECONDS
        ]
        for sid in stale:
            del self._sessions[sid]


# Singleton instance
store = SessionStore()
