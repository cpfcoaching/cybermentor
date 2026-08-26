"""
Chat Route

Handles streaming chat interactions with the CyberMentor agent.
Supports Server-Sent Events (SSE) for real-time streaming responses.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from agent.cybermentor import create_cybermentor_agent
from api.models import ChatRequest, ChatResponse, SessionSummary

router = APIRouter(prefix="/api", tags=["chat"])

# In-memory session store (maps user_id -> session_id for this process)
# In production, this would be backed by Firestore
_SESSION_STORE: dict[str, str] = {}


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream a chat response from CyberMentor using Server-Sent Events.

    The client should use EventSource or fetch with stream reading to consume
    the response. Each chunk is sent as a `data: ...` SSE event.
    The stream ends with `data: [DONE]`.
    """
    # Resolve or create session ID
    session_id = request.session_id
    if not session_id:
        session_id = _SESSION_STORE.get(request.user_id) or str(uuid.uuid4())
    _SESSION_STORE[request.user_id] = session_id

    async def event_generator():
        try:
            async with create_cybermentor_agent(conversation_id=session_id) as agent:
                # Prefix message with user context
                contextualized_message = (
                    f"[User ID: {request.user_id}]\n\n{request.message}"
                )

                response = await agent.chat(contextualized_message)

                # Stream tokens
                async for chunk in response:
                    if chunk:
                        data = json.dumps({"token": chunk, "session_id": session_id})
                        yield f"data: {data}\n\n"
                        await asyncio.sleep(0)  # Yield control to event loop

                # Signal completion
                yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

        except Exception as e:
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
    Non-streaming chat endpoint. Returns the full response at once.
    Use /api/chat/stream for a better user experience in the browser.
    """
    session_id = request.session_id
    if not session_id:
        session_id = _SESSION_STORE.get(request.user_id) or str(uuid.uuid4())
    _SESSION_STORE[request.user_id] = session_id

    try:
        async with create_cybermentor_agent(conversation_id=session_id) as agent:
            contextualized_message = f"[User ID: {request.user_id}]\n\n{request.message}"
            response = await agent.chat(contextualized_message)
            full_response = await response.text()

        return ChatResponse(
            session_id=session_id,
            response=full_response,
            user_id=request.user_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.get("/session/{user_id}", response_model=SessionSummary)
async def get_session(user_id: str):
    """Get the current session info for a user."""
    session_id = _SESSION_STORE.get(user_id, "")
    return SessionSummary(
        user_id=user_id,
        session_id=session_id,
        message_count=0,
        messages=[],
    )
