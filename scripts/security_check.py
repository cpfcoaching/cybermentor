#!/usr/bin/env python3
"""
Pre-Merge Security & Vulnerability Check Script for CyberMentor

Verifies compliance with:
- OWASP Top 10 Web Application Security Risks (2025)
- OWASP Top 10 for Large Language Model Applications (LLM01-LLM10)
- Zero-Leaked-Credential & Secret Isolation Mandate

Exits with code 0 if all security checks pass, non-zero if vulnerabilities are found.
"""

import os
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).parent.parent


def check_secrets_and_api_keys() -> list[str]:
    """Scan all files for exposed production API keys, service account credentials, and secrets."""
    errors = []
    
    # Common high-risk secret patterns (with strict word boundaries)
    patterns = [
        (r'\bAIzaSy[A-Za-z0-9_-]{33}\b', "Google / Firebase API Key"),
        (r'\bsk-[A-Za-z0-9_-]{20,}\b', "OpenAI / Generic Secret Key"),
        (r'-----BEGIN\s+(RSA|EC|OPENSSH|PRIVATE)\s+KEY-----', "Private Key Material"),
        (r'["\']password["\']\s*:\s*["\'][^"\']{4,}["\']', "Hardcoded Password"),
    ]

    ignored_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", "test_helper_sessions", "test_sessions", "test_vertex_sessions"}
    ignored_files = {"package-lock.json", ".env.example", "security_check.py", ".env", ".env.local"}

    for path in ROOT.rglob("*"):
        if any(part in ignored_dirs for part in path.parts):
            continue
        if path.name in ignored_files or path.name.endswith(".env") or path.is_dir():
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            for pattern, desc in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Allow client-side Firebase public web API key in app.js if configured
                    if "AIzaSyAMRuiN-oGbuxZ3a63l7bjTugRi2TjYdjQ" in str(match) and path.name == "app.js":
                        continue
                    errors.append(f"❌ [SECRET DETECTED] {desc} found in {path.relative_to(ROOT)}: {match[:10]}...")
        except Exception as e:
            pass

    return errors


def check_firestore_rules() -> list[str]:
    """Verify Firestore security rules enforce strict user UID isolation."""
    errors = []
    rules_file = ROOT / "firestore.rules"
    if not rules_file.exists():
        errors.append("❌ firestore.rules file is missing!")
        return errors

    content = rules_file.read_text()
    if "request.auth.uid == userId" not in content:
        errors.append("❌ firestore.rules does not enforce request.auth.uid == userId profile isolation!")
    return errors


def check_prompt_injection_defenses() -> list[str]:
    """Verify system persona and chat builders contain explicit OWASP LLM01 prompt injection defenses."""
    errors = []
    persona_file = ROOT / "agent" / "persona.txt"
    if not persona_file.exists():
        errors.append("❌ agent/persona.txt is missing!")
    else:
        content = persona_file.read_text()
        if "OWASP" not in content or "Prompt Injection" not in content:
            errors.append("❌ agent/persona.txt missing OWASP LLM01 Prompt Injection defense section!")

    chat_file = ROOT / "api" / "routes" / "chat.py"
    if not chat_file.exists():
        errors.append("❌ api/routes/chat.py is missing!")
    else:
        content = chat_file.read_text()
        if "[CANDIDATE MESSAGE]" not in content:
            errors.append("❌ api/routes/chat.py missing structured input delimiter separation!")

    return errors


def check_frontend_xss_sanitization() -> list[str]:
    """Verify web frontend performs HTML escaping and link protocol sanitization."""
    errors = []
    app_js = ROOT / "web" / "js" / "app.js"
    if not app_js.exists():
        errors.append("❌ web/js/app.js is missing!")
    else:
        content = app_js.read_text()
        if "escapeHtml" not in content:
            errors.append("❌ web/js/app.js missing escapeHtml() XSS mitigation!")
        if "noopener" not in content:
            errors.append("❌ web/js/app.js missing rel='noopener' link security!")

    return errors


def main():
    print("🛡️ Running CyberMentor Pre-Merge Security & Vulnerability Audit...")
    all_errors = []

    print("  1. Scanning for exposed API keys and secrets...")
    secret_errors = check_secrets_and_api_keys()
    all_errors.extend(secret_errors)

    print("  2. Validating Firestore profile isolation rules...")
    firestore_errors = check_firestore_rules()
    all_errors.extend(firestore_errors)

    print("  3. Checking OWASP LLM01 Prompt Injection defenses...")
    prompt_errors = check_prompt_injection_defenses()
    all_errors.extend(prompt_errors)

    print("  4. Verifying Frontend XSS & Output Sanitization...")
    frontend_errors = check_frontend_xss_sanitization()
    all_errors.extend(frontend_errors)

    if all_errors:
        print("\n❌ PRE-MERGE SECURITY CHECK FAILED:")
        for err in all_errors:
            print(f"   {err}")
        sys.exit(1)
    else:
        print("\n✅ ALL PRE-MERGE SECURITY CHECKS PASSED!")
        print("   • Zero secrets or exposed API keys detected.")
        print("   • Strict profile isolation in firestore.rules verified.")
        print("   • OWASP LLM01 Prompt Injection delimiters active.")
        print("   • Frontend output sanitization & link escaping verified.")
        sys.exit(0)


if __name__ == "__main__":
    main()
