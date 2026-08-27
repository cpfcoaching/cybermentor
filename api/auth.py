"""
Google SSO & Firebase Authentication Middleware / Verification

Verifies Google ID Tokens and Firebase Authentication ID Tokens (with MFA support)
from the HTTP Authorization header (Bearer <ID_TOKEN>).
"""

import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import google.auth.transport.requests
import google.oauth2.id_token

logger = logging.getLogger(__name__)

security_bearer = HTTPBearer(auto_error=False)


def verify_google_id_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a Google OAuth or Firebase Auth ID Token.
    Returns decoded token dictionary if valid.
    """
    if not token or token == "anonymous":
        return None
    try:
        req = google.auth.transport.requests.Request()
        # Try verifying token
        decoded = google.oauth2.id_token.verify_firebase_token(token, req)
        return decoded
    except Exception as e1:
        try:
            req = google.auth.transport.requests.Request()
            decoded = google.oauth2.id_token.verify_oauth2_token(token, req)
            return decoded
        except Exception as e2:
            logger.debug(f"ID Token verification note: {e1} | {e2}")
            return None


async def get_optional_authenticated_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication dependency.
    If Bearer token is provided, verifies it and returns user claims dict.
    """
    if not credentials or not credentials.credentials:
        return None
    token = credentials.credentials
    return verify_google_id_token(token)
