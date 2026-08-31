"""
Chat Route

Handles streaming chat interactions with the CyberMentor agent.
Supports Server-Sent Events (SSE) for real-time streaming responses.
"""

import asyncio
import json
import logging
import os
import pathlib
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse

from api.models import ChatRequest, ChatResponse, SessionSummary
from api.services.resume_parser import parse_resume_bytes
from agent.cybermentor import create_cybermentor_agent
from agent.tools.progress_tracker import get_user_progress
from agent.tools.conversation_store import save_conversation_message, get_conversation_history
from agent.tools.ace_memory import get_agent_memory, analyze_conversation_for_skills, get_documented_candidate_skills
from agent.tools.gemma_analyzer import classify_user_intent

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


def _build_contextualized_prompt(user_id: str, message: str, gemma_intent: str | None = None) -> str:
    """
    Build a prompt that injects the user's persistent progress history, active resume profile,
    target career track, Gemma pre-routed intent classification, and ACE cognitive memory notes & documented skills into context.
    """
    from api.routes.resume import get_user_resume_from_storage
    
    history_ctx = get_user_progress(user_id)
    memory_ctx = get_agent_memory(user_id)
    
    # Retrieve cumulative documented skills from ACE memory
    doc_skills = get_documented_candidate_skills(user_id)
    skills_summary = ""
    if doc_skills:
        skill_names = [s.get("skill_name", "") for s in doc_skills if s.get("skill_name")]
        skills_summary = f"[ACE DOCUMENTED CANDIDATE SKILLS]: {', '.join(skill_names)}\n"

    # Retrieve candidate's active resume and target role
    resume_record = get_user_resume_from_storage(user_id)
    resume_ctx = ""
    if resume_record and resume_record.get("markdown_text"):
        c_name = resume_record.get("candidate_name", "Candidate")
        t_role = resume_record.get("target_role", "Enterprise CISO / Executive Advisory")
        raw_text = resume_record.get("markdown_text", "")
        resume_ctx = (
            f"[ACTIVE CANDIDATE PROFILE ON FILE]:\n"
            f"Candidate Name: {c_name}\n"
            f"Target Career Track: {t_role}\n"
            f"Profile Resume Highlights: {raw_text[:800]}...\n"
        )

    intent_info = f"[GEMMA INTENT CLASSIFICATION PRE-ROUTING]: {gemma_intent}\n" if gemma_intent else ""
    return (
        f"[SYSTEM CONTEXT FOR CANDIDATE PROFILE '{user_id}']\n"
        f"{intent_info}"
        f"{resume_ctx}"
        f"{skills_summary}"
        f"{history_ctx}\n\n"
        f"{memory_ctx}\n\n"
        f"[STRATEGIC ALIGNMENT DIRECTIVE]: You already have full access to this candidate's history, target track, verified skills, and resume. "
        f"Whenever the candidate asks to review or update their profile/goals, summarize what you know about their background and target track, evaluate how well their experience aligns with their goals, and guide their next calibration.\n\n"
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
            # Continually mine and document candidate skills from conversation turn into ACE memory
            try:
                analyze_conversation_for_skills(request.user_id, request.message, source="text_conversation")
            except Exception as se:
                logger.warning(f"ACE conversation skill extraction error: {se}")

            # Gemma 3 27B Fast Pre-Routing Intent Classification
            try:
                gemma_intent = classify_user_intent(request.message)
            except Exception as ge:
                logger.warning(f"Gemma pre-routing intent classification fallback: {ge}")
                gemma_intent = None

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
                    request.user_id, request.message, gemma_intent
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
        try:
            analyze_conversation_for_skills(request.user_id, request.message, source="text_conversation")
        except Exception as se:
            logger.warning(f"ACE conversation skill extraction error: {se}")

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
@router.get("/chat/history/{user_id}")
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


@router.get("/auth/config")
async def get_auth_config():
    """Return public client Firebase Auth SDK configuration."""
    api_key = os.getenv("FIREBASE_WEB_API_KEY", "")
    return {
        "projectId": os.getenv("GOOGLE_CLOUD_PROJECT", "cybermentor-506813"),
        "appId": os.getenv("FIREBASE_APP_ID", "1:1019457807345:web:8eb4c313f720600b8bda50"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "cybermentor-506813.firebasestorage.app"),
        "apiKey": api_key,
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "cybermentor-506813.firebaseapp.com"),
    }


@router.post("/resume/parse")
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse uploaded resume document (PDF, Word DOCX, TXT, MD) and return clean plain text.
    """
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        text = parse_resume_bytes(content, file.filename or "resume.pdf")
        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from document. Ensure the file contains readable text."
            )
        return {
            "filename": file.filename,
            "text": text.strip(),
            "character_count": len(text.strip()),
            "word_count": len(text.strip().split()),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing resume upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Document parsing error: {str(e)}")

