"""
Chat Route

Handles streaming chat interactions with the CyberMentor agent.
Supports Server-Sent Events (SSE) for real-time streaming responses.
"""

import asyncio
import json
import logging
import pathlib
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from agent.cybermentor import create_cybermentor_agent
from agent.tools.ace_memory import get_agent_memory
from agent.tools.progress_tracker import get_user_progress
from agent.tools.conversation_store import save_conversation_message, get_conversation_history
from api.models import ChatRequest, ChatResponse, SessionSummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

# In-memory session store (maps user_id -> session_id for this process)
_SESSION_STORE: dict[str, str] = {}


def _session_file_exists(save_dir: pathlib.Path, session_id: str) -> bool:
    """Check if a session file for session_id exists on disk."""
    if not session_id or not save_dir.exists():
        return False
    clean_id = session_id.replace("-", "")
    try:
        for f in save_dir.iterdir():
            if clean_id in f.name or session_id in f.name:
                return True
    except Exception:
        pass
    return False


def _build_contextualized_prompt(user_id: str, message: str) -> str:
    """
    Build a prompt that injects the user's persistent progress history
    and ACE long-term cognitive memory notes into the message context.
    """
    history_ctx = get_user_progress(user_id)
    memory_ctx = get_agent_memory(user_id)
    return (
        f"[SYSTEM CONTEXT FOR CANDIDATE PROFILE '{user_id}']\n"
        f"{history_ctx}\n\n"
        f"{memory_ctx}\n\n"
        f"[IMPORTANT INSTRUCTION]: You already know this candidate's history, goals, and notes. "
        f"Do NOT ask generic questions about experience level if already known above.\n\n"
        f"[CANDIDATE MESSAGE]:\n{message}"
    )


@asynccontextmanager
async def get_cybermentor_agent(session_id: str | None = None):
    """
    Safely acquire a CyberMentor agent context manager.
    Resumes an existing session if session_id's file exists on disk,
    otherwise creates a fresh session without failing.
    """
    save_dir = pathlib.Path(__file__).parent.parent.parent / "sessions"
    save_dir.mkdir(parents=True, exist_ok=True)

    if session_id and _session_file_exists(save_dir, session_id):
        try:
            agent = create_cybermentor_agent(conversation_id=session_id)
            async with agent as active_agent:
                yield active_agent, session_id
                return
        except Exception as e:
            logger.warning(f"Could not resume session {session_id}: {e}. Creating new session.")

    # Fallback or brand new session
    agent = create_cybermentor_agent()
    async with agent as active_agent:
        actual_id = session_id or str(uuid.uuid4())
        yield active_agent, actual_id


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream a chat response from CyberMentor using Server-Sent Events.
    Persists to Cloud Firestore ONLY if request is from an authenticated user (is_guest=False).
    For guest sessions, ACE memory operates in-memory for the turn.
    """
    session_id = request.session_id or _SESSION_STORE.get(request.user_id)

    async def event_generator():
        try:
            async with get_cybermentor_agent(session_id) as (agent, active_session_id):
                _SESSION_STORE[request.user_id] = active_session_id

                # Save candidate message to Cloud Firestore if authenticated (not guest)
                if not request.is_guest:
                    save_conversation_message(
                        user_id=request.user_id,
                        session_id=active_session_id,
                        role="user",
                        content=request.message,
                    )

                contextualized_message = _build_contextualized_prompt(
                    request.user_id, request.message
                )

                response = await agent.chat(contextualized_message)

                full_response_chunks = []
                async for chunk in response:
                    if chunk:
                        full_response_chunks.append(chunk)
                        data = json.dumps({"token": chunk, "session_id": active_session_id})
                        yield f"data: {data}\n\n"
                        await asyncio.sleep(0)

                full_model_response = "".join(full_response_chunks)
                if full_model_response and not request.is_guest:
                    # Save assistant response to Cloud Firestore if authenticated
                    save_conversation_message(
                        user_id=request.user_id,
                        session_id=active_session_id,
                        role="model",
                        content=full_model_response,
                    )

                yield f"data: {json.dumps({'done': True, 'session_id': active_session_id})}\n\n"

        except Exception as e:
            logger.error(f"Chat stream error: {e}", exc_info=True)
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Non-streaming chat endpoint. Persists message turn to Cloud Firestore.
    """
    session_id = request.session_id or _SESSION_STORE.get(request.user_id)

    try:
        async with get_cybermentor_agent(session_id) as (agent, active_session_id):
            _SESSION_STORE[request.user_id] = active_session_id

            save_conversation_message(
                user_id=request.user_id,
                session_id=active_session_id,
                role="user",
                content=request.message,
            )

            contextualized_message = _build_contextualized_prompt(
                request.user_id, request.message
            )
            response = await agent.chat(contextualized_message)
            full_response = await response.text()

            save_conversation_message(
                user_id=request.user_id,
                session_id=active_session_id,
                role="model",
                content=full_response,
            )

        return ChatResponse(
            session_id=active_session_id,
            response=full_response,
            user_id=request.user_id,
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.get("/history/{user_id}")
async def get_history(user_id: str, session_id: str | None = None):
    """
    Retrieve past conversation messages for a user from Cloud Firestore database.
    """
    messages = get_conversation_history(user_id=user_id, session_id=session_id)
    return {
        "user_id": user_id,
        "session_id": session_id or _SESSION_STORE.get(user_id, ""),
        "messages": messages,
        "count": len(messages),
    }


@router.get("/session/{user_id}", response_model=SessionSummary)
async def get_session(user_id: str):
    """Get the current session info and history count for a user."""
    session_id = _SESSION_STORE.get(user_id, "")
    messages = get_conversation_history(user_id=user_id, session_id=session_id)
    return SessionSummary(
        user_id=user_id,
        session_id=session_id,
        message_count=len(messages),
        messages=[],
    )
