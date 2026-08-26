"""
Study Planner Tool

Generates structured, week-by-week study plans for cybersecurity certifications.
"""

import json
import pathlib

_DATA_DIR = pathlib.Path(__file__).parent.parent.parent / "data" / "knowledge"

# Cert-specific durations (hours) and phase breakdown
_CERT_METADATA = {
    "security+": {"total_hours": 120, "vendor": "CompTIA", "difficulty": "Beginner"},
    "cysa+": {"total_hours": 150, "vendor": "CompTIA", "difficulty": "Intermediate"},
    "casp+": {"total_hours": 200, "vendor": "CompTIA", "difficulty": "Advanced"},
    "ceh": {"total_hours": 160, "vendor": "EC-Council", "difficulty": "Intermediate"},
    "cissp": {"total_hours": 250, "vendor": "ISC2", "difficulty": "Advanced"},
    "ejpt": {"total_hours": 80, "vendor": "eLearnSecurity", "difficulty": "Beginner"},
    "oscp": {"total_hours": 400, "vendor": "Offensive Security", "difficulty": "Advanced"},
    "aws security specialty": {"total_hours": 120, "vendor": "AWS", "difficulty": "Intermediate"},
    "gcp security": {"total_hours": 100, "vendor": "Google", "difficulty": "Intermediate"},
}


def generate_study_plan(
    target_cert: str,
    hours_per_week: int,
    current_level: str = "beginner",
) -> str:
    """Generate a week-by-week study plan for a cybersecurity certification.

    Use this tool when a user asks how to study for a specific certification,
    wants a study schedule, or asks "how long will it take to get my [cert]?"

    Args:
        target_cert: The certification to study for. Examples: "Security+",
                     "CISSP", "OSCP", "CEH", "eJPT", "CySA+".
        hours_per_week: How many hours per week the user can dedicate to studying.
                        Should be between 1 and 40.
        current_level: The user's current experience level. One of: "beginner",
                       "intermediate", "advanced".

    Returns:
        A formatted week-by-week study plan as a string.
    """
    cert_key = target_cert.lower().strip()
    meta = _CERT_METADATA.get(cert_key)

    if not meta:
        # Fallback for unknown certs
        total_hours = 150
        vendor = "Unknown"
        difficulty = "Unknown"
    else:
        total_hours = meta["total_hours"]
        vendor = meta["vendor"]
        difficulty = meta["difficulty"]

    # Adjust hours for current level
    level_multiplier = {"beginner": 1.3, "intermediate": 1.0, "advanced": 0.8}
    adjusted_hours = int(total_hours * level_multiplier.get(current_level, 1.0))

    hours_per_week = max(1, min(hours_per_week, 40))
    total_weeks = max(1, adjusted_hours // hours_per_week)

    # Divide into phases
    phase1_weeks = max(1, int(total_weeks * 0.30))  # Foundations
    phase2_weeks = max(1, int(total_weeks * 0.40))  # Core domains
    phase3_weeks = max(1, int(total_weeks * 0.20))  # Practice exams
    phase4_weeks = max(1, total_weeks - phase1_weeks - phase2_weeks - phase3_weeks)  # Review/buffer

    plan = f"""## 📅 Study Plan: {target_cert.title()} ({vendor})

**Your Profile**
- Experience Level: {current_level.title()}
- Study Hours/Week: {hours_per_week}h
- Estimated Duration: ~{total_weeks} weeks ({adjusted_hours} total hours)
- Exam Difficulty: {difficulty}

---

### Phase 1 — Foundations (Weeks 1–{phase1_weeks})
**Goal:** Build the conceptual foundation before diving into exam-specific content.
- [ ] Watch overview videos on YouTube / Professor Messer (free)
- [ ] Read the official exam objectives document (download from vendor site)
- [ ] Set up a study journal or Notion page to track your notes
- [ ] Join the r/CompTIA or relevant Discord community
- **Hours/week:** {hours_per_week}h → Focus 70% content, 30% notes

### Phase 2 — Core Domain Study (Weeks {phase1_weeks + 1}–{phase1_weeks + phase2_weeks})
**Goal:** Work through every exam domain systematically.
- [ ] Use the official study guide or a reputable book (e.g., Mike Chapple for CISSP, Mike Myers for Security+)
- [ ] Take chapter quizzes as you go — aim for 80%+ before moving on
- [ ] Build a lab environment (TryHackMe, HackTheBox, or local VMs) for hands-on practice
- [ ] Create flashcards (Anki) for acronyms, ports, protocols
- **Hours/week:** {hours_per_week}h → Split evenly across domains

### Phase 3 — Practice Exams (Weeks {phase1_weeks + phase2_weeks + 1}–{phase1_weeks + phase2_weeks + phase3_weeks})
**Goal:** Simulate exam conditions and identify weak areas.
- [ ] Take at least 3 full-length practice exams (Jason Dion on Udemy is excellent)
- [ ] Review every wrong answer — understand WHY, not just the correct answer
- [ ] Re-study any domain where you score below 75%
- [ ] Time yourself: practice finishing in the allotted exam time
- **Target:** Consistent 85%+ on practice exams before scheduling the real thing

### Phase 4 — Final Review & Exam Week (Weeks {total_weeks - phase4_weeks + 1}–{total_weeks})
**Goal:** Reinforce weak spots, manage exam anxiety, and sit the exam.
- [ ] Review your Anki flashcards daily
- [ ] Do one final practice exam 3 days before the exam
- [ ] Rest 2 days before — trust your preparation
- [ ] Schedule your exam at the start of this phase if you haven't already

---

### 📚 Recommended Resources for {target_cert.title()}
- **Free:** Professor Messer (YouTube + free notes), TryHackMe paths
- **Paid:** Jason Dion (Udemy practice exams), Mike Chapple/Darril Gibson books
- **Community:** r/CompTIA, Breaking Into Cyber Discord

### ⚡ Quick Tips
1. Consistency beats intensity — 1 hour every day beats 7 hours on Sunday
2. Don't just read — do labs, write notes, teach concepts back to yourself
3. When you're ready to schedule, do it. Having a deadline creates urgency.

---
*Study plan generated by CyberMentor — Breaking Into Cyber*"""

    return plan
