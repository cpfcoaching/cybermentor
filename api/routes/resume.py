"""
Resume Routes — CyberMentor

Endpoints for saving user's reviewed & updated resumes, retrieving the latest
resume draft, and exporting high-impact Word (.docx) and PDF (.pdf) documents.
"""

import json
import os
import pathlib
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Response, Query
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field

from api.services.resume_exporter import generate_docx_resume, generate_pdf_resume

logger = logging.getLogger("cybermentor.resume_routes")

router = APIRouter(prefix="/api/resume", tags=["resume"])

_LOCAL_RESUME_STORAGE = pathlib.Path(__file__).parent.parent.parent / "sessions" / "resumes"


class ResumeSaveRequest(BaseModel):
    user_id: str = Field(..., description="User ID or session identifier")
    markdown_text: str = Field(..., description="Full updated resume markdown text")
    target_role: Optional[str] = Field("general", description="Target cybersecurity role track")
    candidate_name: Optional[str] = Field(None, description="Candidate name")


class ResumeExportRequest(BaseModel):
    markdown_text: str = Field(..., description="Full updated resume markdown text")
    filename: Optional[str] = Field("Cybersecurity_Resume", description="Base filename for download")
    target_role: Optional[str] = Field("general", description="Target cybersecurity role track")


def _get_firestore():
    """Try to get Firestore client."""
    try:
        from google.cloud import firestore
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project:
            return None
        return firestore.Client(project=project)
    except Exception:
        return None


def _local_resume_path(user_id: str) -> pathlib.Path:
    safe = "".join(c for c in user_id if c.isalnum() or c in "-_")
    return _LOCAL_RESUME_STORAGE / f"{safe}.json"


def save_user_resume_to_storage(user_id: str, markdown_text: str, target_role: str = "general", candidate_name: str = None) -> dict:
    """Store the latest resume draft in Firestore and local fallback."""
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "user_id": user_id,
        "markdown_text": markdown_text,
        "target_role": target_role,
        "candidate_name": candidate_name or "Candidate",
        "updated_at": timestamp
    }

    db = _get_firestore()
    if db:
        try:
            db.collection("users").document(user_id).collection("resumes").document("latest").set(record)
        except Exception as e:
            logger.warning(f"Failed to save resume to Firestore for {user_id}: {e}")

    _LOCAL_RESUME_STORAGE.mkdir(parents=True, exist_ok=True)
    path = _local_resume_path(user_id)
    try:
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    except Exception as e:
        logger.warning(f"Failed to save resume to local path for {user_id}: {e}")

    return record


def get_user_resume_from_storage(user_id: str) -> Optional[dict]:
    """Retrieve the latest resume draft from Firestore or local fallback."""
    db = _get_firestore()
    if db:
        try:
            doc = db.collection("users").document(user_id).collection("resumes").document("latest").get()
            if doc.exists:
                return doc.to_dict()
        except Exception:
            pass

    path = _local_resume_path(user_id)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


@router.post("/save")
async def save_resume(request: ResumeSaveRequest):
    """Save the updated resume text to the candidate's profile."""
    record = save_user_resume_to_storage(
        user_id=request.user_id,
        markdown_text=request.markdown_text,
        target_role=request.target_role,
        candidate_name=request.candidate_name
    )
    return {"status": "saved", "updated_at": record["updated_at"]}


@router.get("/{user_id}/latest")
async def get_latest_resume(user_id: str):
    """Retrieve the user's latest saved resume draft."""
    record = get_user_resume_from_storage(user_id)
    if not record:
        return {"found": False, "markdown_text": "", "message": "No updated resume saved yet."}
    return {
        "found": True,
        "markdown_text": record.get("markdown_text", ""),
        "target_role": record.get("target_role", "general"),
        "candidate_name": record.get("candidate_name", "Candidate"),
        "updated_at": record.get("updated_at", "")
    }


@router.post("/export/docx")
async def export_docx(request: ResumeExportRequest):
    """Generate and download a styled Microsoft Word (.docx) document."""
    if not request.markdown_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")

    clean_filename = "".join(c for c in request.filename if c.isalnum() or c in "-_.")
    if not clean_filename.endswith(".docx"):
        clean_filename += ".docx"

    docx_bytes = generate_docx_resume(request.markdown_text, filename=clean_filename)

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{clean_filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.post("/export/pdf")
async def export_pdf(request: ResumeExportRequest):
    """Generate and download a styled PDF (.pdf) document."""
    if not request.markdown_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")

    clean_filename = "".join(c for c in request.filename if c.isalnum() or c in "-_.")
    if not clean_filename.endswith(".pdf"):
        clean_filename += ".pdf"

    pdf_bytes = generate_pdf_resume(request.markdown_text, filename=clean_filename)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{clean_filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.get("/{user_id}/download/docx")
async def download_user_docx(user_id: str, filename: Optional[str] = "Cybersecurity_Resume.docx"):
    """Direct one-click download of the user's latest saved resume as DOCX."""
    record = get_user_resume_from_storage(user_id)
    if not record or not record.get("markdown_text"):
        raise HTTPException(status_code=404, detail="No updated resume found for this profile. Please review and update your resume first.")

    docx_bytes = generate_docx_resume(record["markdown_text"], filename=filename)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.get("/{user_id}/download/pdf")
async def download_user_pdf(user_id: str, filename: Optional[str] = "Cybersecurity_Resume.pdf"):
    """Direct one-click download of the user's latest saved resume as PDF."""
    record = get_user_resume_from_storage(user_id)
    if not record or not record.get("markdown_text"):
        raise HTTPException(status_code=404, detail="No updated resume found for this profile. Please review and update your resume first.")

    pdf_bytes = generate_pdf_resume(record["markdown_text"], filename=filename)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
