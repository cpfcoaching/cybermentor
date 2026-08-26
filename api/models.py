"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    user_id: str = Field(..., min_length=1, max_length=64, description="User's session identifier")
    message: str = Field(..., min_length=1, max_length=8000, description="The user's message")
    session_id: Optional[str] = Field(None, description="Existing session ID to resume. If None, a new session is created.")


class ChatResponse(BaseModel):
    """Response from the chat endpoint (non-streaming)."""
    session_id: str
    response: str
    user_id: str


class MilestoneRequest(BaseModel):
    """Request to manually log a milestone."""
    milestone: str = Field(..., min_length=1, max_length=256)
    notes: Optional[str] = Field("", max_length=1024)


class MilestoneItem(BaseModel):
    """A single progress milestone."""
    milestone: str
    notes: Optional[str] = ""
    timestamp: str


class ProgressResponse(BaseModel):
    """User's full progress history."""
    user_id: str
    total_milestones: int
    milestones: list[MilestoneItem]


class SessionSummary(BaseModel):
    """Summary of a user session."""
    user_id: str
    session_id: str
    message_count: int
    messages: list[dict]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
