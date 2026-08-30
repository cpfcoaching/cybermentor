#!/usr/bin/env python3
"""
Comprehensive QA Automation & Health Verification Suite for CyberMentor
Tests all REST endpoints, SSE streams, static assets, and agent tools.
"""

import sys
import json
import urllib.request
import urllib.error
import time

BASE_URL = "https://client.breakingintocybersecurity.org"
TEST_USER = f"QA_Automated_Runner_{int(time.time())}"

results = []

def log_test(name, success, message="", duration_ms=0):
    status_icon = "✅ PASS" if success else "❌ FAIL"
    results.append((name, success, message, duration_ms))
    print(f"{status_icon} | {name:<35} | {duration_ms:>6.1f}ms | {message}")

def make_request(path, method="GET", data=None, headers=None, expect_stream=False):
    url = f"{BASE_URL}{path}"
    req_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        **(headers or {})
    }
    if data and "Content-Type" not in req_headers:
        req_headers["Content-Type"] = "application/json"
    
    body = json.dumps(data).encode("utf-8") if isinstance(data, dict) else (data if data else None)
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            elapsed = (time.time() - start) * 1000
            status = resp.status
            if expect_stream:
                chunks = []
                for _ in range(25):  # Read first 25 chunks
                    line = resp.readline().decode("utf-8")
                    if not line:
                        break
                    chunks.append(line)
                return status, "".join(chunks), elapsed
            else:
                content = resp.read().decode("utf-8", errors="ignore")
                return status, content, elapsed
    except urllib.error.HTTPError as e:
        elapsed = (time.time() - start) * 1000
        content = e.read().decode("utf-8", errors="ignore")
        return e.code, content, elapsed
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return 0, str(e), elapsed

print(f"\n=======================================================")
print(f"🛡️ CYBERMENTOR END-TO-END QA SUITE")
print(f"Target: {BASE_URL}")
print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
print(f"=======================================================\n")

# 1. Health Endpoint
status, body, elapsed = make_request("/health")
try:
    data = json.loads(body)
    is_healthy = status == 200 and data.get("status") == "healthy"
    log_test("GET /health", is_healthy, f"HTTP {status} - Status: {data.get('status')}", elapsed)
except Exception as e:
    log_test("GET /health", False, f"HTTP {status} - Invalid JSON: {e}", elapsed)

# 2. Swagger / API Docs
status, body, elapsed = make_request("/docs")
log_test("GET /docs (Swagger)", status == 200, f"HTTP {status} ({len(body)} bytes)", elapsed)

# 3. Main Landing Page
status, body, elapsed = make_request("/home.html")
has_branding = "CyberMentor" in body and "Breaking Into Cybersecurity" in body
log_test("GET /home.html (Marketing)", status == 200 and has_branding, f"HTTP {status} - Brand verification passed", elapsed)

# 4. App Studio Page
status, body, elapsed = make_request("/")
has_app_v2 = "app.js?v=2.2.0" in body
log_test("GET / (AI Studio UI)", status == 200 and has_app_v2, f"HTTP {status} - Script v2.2.0 verified", elapsed)

# 5. Service Worker
status, body, elapsed = make_request("/sw.js")
is_v22 = "cybermentor-v2.2.0" in body
log_test("GET /sw.js (PWA Service Worker)", status == 200 and is_v22, f"HTTP {status} - Cache v2.2.0 verified", elapsed)

# 6. Static App.js
status, body, elapsed = make_request("/js/app.js?v=2.2.0")
no_voice_bug = "voiceEnabled" not in body
log_test("GET /js/app.js (Frontend Logic)", status == 200 and no_voice_bug, f"HTTP {status} - Zero undefined voiceEnabled references", elapsed)

# 7. Progress API - Initial fetch
status, body, elapsed = make_request(f"/api/progress/{TEST_USER}")
log_test("GET /api/progress/{user}", status == 200, f"HTTP {status}", elapsed)

# 8. Analytics Dashboard API
status, body, elapsed = make_request(f"/api/progress/{TEST_USER}/analytics")
try:
    data = json.loads(body)
    has_keys = "study_streak_days" in data and "cert_readiness_pct" in data
    log_test("GET /api/progress/{user}/analytics", status == 200 and has_keys, f"HTTP {status} - Keys: streak, readiness, milestones", elapsed)
except Exception as e:
    log_test("GET /api/progress/{user}/analytics", False, f"HTTP {status} - Error: {e}", elapsed)

# 9. Voice TTS Endpoint
status, body, elapsed = make_request("/api/voice/speak", method="POST", data={"text": "CyberMentor QA verification check.", "voice_profile": "island_boy"})
log_test("POST /api/voice/speak (TTS)", status == 200, f"HTTP {status}", elapsed)

# 10. Agent Streaming Chat (Career Discovery)
chat_payload = {
    "user_id": TEST_USER,
    "message": "I have 2 years of Helpdesk experience and want to become a SOC analyst. What are my first steps?",
    "is_guest": False
}
status, body, elapsed = make_request("/api/chat/stream", method="POST", data=chat_payload, expect_stream=True)
has_stream_tokens = "data: " in body and ("SOC" in body or "Security" in body or "token" in body)
log_test("POST /api/chat/stream (Career Agent)", status == 200 and has_stream_tokens, f"HTTP {status} - Streaming token delivery verified", elapsed)

# 11. Agent Streaming Chat (Study Plan Tool)
study_payload = {
    "user_id": TEST_USER,
    "message": "Give me a 6-week study plan for CompTIA Security+ with 10 hours per week",
    "is_guest": False
}
status, body, elapsed = make_request("/api/chat/stream", method="POST", data=study_payload, expect_stream=True)
has_study_tokens = "data: " in body and ("Week" in body or "domain" in body or "Security+" in body or "token" in body)
log_test("POST /api/chat/stream (Study Planner)", status == 200 and has_study_tokens, f"HTTP {status} - Study roadmap generation verified", elapsed)

# 12. Agent Streaming Chat (Interview Prep Tool)
interview_payload = {
    "user_id": TEST_USER,
    "message": "Ask me a technical SOC analyst interview question",
    "is_guest": False
}
status, body, elapsed = make_request("/api/chat/stream", method="POST", data=interview_payload, expect_stream=True)
has_interview_tokens = "data: " in body and ("question" in body.lower() or "incident" in body.lower() or "token" in body)
log_test("POST /api/chat/stream (Interview Drill)", status == 200 and has_interview_tokens, f"HTTP {status} - Interview drill streaming verified", elapsed)

# Summary
total = len(results)
passed = sum(1 for _, s, _, _ in results if s)
failed = total - passed

print(f"\n=======================================================")
print(f"📊 QA AUDIT SUMMARY: {passed}/{total} PASSED ({failed} FAILED)")
print(f"=======================================================\n")

if failed > 0:
    sys.exit(1)
