"""
Skill & Certification Mindmap Explorer Tool

Provides structured mindmaps of skills and certifications for cybersecurity roles,
and computes transferable skill intersections between any source and target job roles.
"""

import json
import pathlib
from typing import Optional

_DATA_DIR = pathlib.Path(__file__).parent.parent.parent / "data" / "knowledge"


def _load_mindmap_data() -> dict:
    """Load the role mindmap and transferable skills ontology."""
    path = _DATA_DIR / "role_mindmaps.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_role_mindmap(role: str, view_type: str = "all") -> str:
    """Generate a structured mindmap of skills and certifications required for a specific cybersecurity job role.

    Use this tool when a user asks:
    - "What skills do I need for a SOC analyst / Pen tester / Cloud Security role?"
    - "Show me a mindmap or breakdown of skills and certs for [role]"
    - "What is the certification roadmap for [role]?"

    Args:
        role: The role to generate a mindmap for (e.g. "soc_analyst", "penetration_tester",
              "cloud_security", "grc", "it_helpdesk", "ciso", "dfir").
        view_type: What to include: "skills", "certs", or "all" (default).

    Returns:
        A structured mindmap with hierarchical categories, core tooling, and cert tiers.
    """
    data = _load_mindmap_data()
    roles = data.get("roles", {})

    clean_key = role.lower().strip().replace(" ", "_").replace("-", "_")
    matched_role = None

    if clean_key in roles:
        matched_role = roles[clean_key]
    else:
        for k, v in roles.items():
            if clean_key in k or k in clean_key or clean_key in v.get("title", "").lower():
                matched_role = v
                break

    if not matched_role:
        available = ", ".join(r.get("title", k) for k, r in roles.items())
        return (
            f"## 🗺️ Mindmap for '{role}'\n\n"
            f"Role not found in the curated matrix. Available roles: {available}.\n"
            f"Please refine your query or ask for one of the primary tracks."
        )

    title = matched_role.get("title", role.title())
    category = matched_role.get("category", "Cybersecurity")
    skills = matched_role.get("skills_mindmap", {})
    certs = matched_role.get("certs_mindmap", {})

    lines = [f"## 🧠 {title} — Skills & Certifications Mindmap", f"*Domain Category: {category}*", ""]

    if view_type in ("skills", "all"):
        lines.append("### 🛠️ Core Skills Mindmap")
        for domain, skill_list in skills.items():
            domain_label = domain.replace("_", " ").title()
            lines.append(f"#### 📍 {domain_label}")
            for s in skill_list:
                lines.append(f"  • {s}")
            lines.append("")

    if view_type in ("certs", "all"):
        lines.append("### 🎓 Certification Mindmap & Progression")
        for tier, cert_list in certs.items():
            tier_label = tier.replace("_", " ").title()
            lines.append(f"  **[{tier_label}]**: {', '.join(cert_list)}")
        lines.append("")

    lines.append("---")
    lines.append(f"💡 *Tip: Ask 'How do I transfer skills from {title} to another role?' to see intersection mapping.*")

    return "\n".join(lines)


def explore_skill_transfer(source_role: str, target_role: str) -> str:
    """Analyze how skills transfer from a candidate's current background to a target cybersecurity role.

    Use this tool when a user asks:
    - "How do I transition from IT helpdesk / SysAdmin / Developer to SOC Analyst / Cloud Security?"
    - "What skills transfer from [role A] to [role B]?"
    - "What is my skill gap moving from [current role] to [dream role]?"

    Args:
        source_role: The user's current background (e.g. "it_helpdesk", "soc_analyst", "penetration_tester", "grc").
        target_role: The desired destination role (e.g. "soc_analyst", "cloud_security", "dfir", "penetration_tester", "ciso").

    Returns:
        Detailed transferable skills breakdown, bridge skills, delta skill gaps to close,
        recommended bridge certifications, and estimated transition timeline.
    """
    data = _load_mindmap_data()
    roles = data.get("roles", {})

    def find_role(name: str):
        k_clean = name.lower().strip().replace(" ", "_").replace("-", "_")
        if k_clean in roles:
            return k_clean, roles[k_clean]
        for k, v in roles.items():
            if k_clean in k or k in k_clean or k_clean in v.get("title", "").lower():
                return k, v
        return None, None

    src_key, src_data = find_role(source_role)
    tgt_key, tgt_data = find_role(target_role)

    if not src_data or not tgt_data:
        return (
            f"## 🔀 Skill Transfer: {source_role} ➔ {target_role}\n\n"
            f"Could not map one or both roles. Supported roles include: "
            f"IT Helpdesk, SOC Analyst, Penetration Tester, Cloud Security, GRC Analyst, DFIR Specialist, CISO."
        )

    src_title = src_data.get("title", source_role)
    tgt_title = tgt_data.get("title", target_role)

    matrix = src_data.get("transferable_matrix", {}).get(tgt_key)

    lines = [
        f"## 🔀 Transferable Skills & Transition Roadmap",
        f"### **{src_title}** ➔ **{tgt_title}**",
        "",
    ]

    if matrix:
        score = matrix.get("compatibility_score", 70)
        diff = matrix.get("difficulty", "Moderate")
        timeline = matrix.get("timeline", "6 months")
        shared = matrix.get("shared_skills", [])
        bridge = matrix.get("bridge_skills", [])
        delta = matrix.get("delta_skills_needed", [])
        certs = matrix.get("recommended_bridge_certs", [])
        advice = matrix.get("breaking_into_cyber_advice", "")

        lines.extend([
            f"| Metric | Assessment |",
            f"|---|---|",
            f"| **Compatibility Match** | **{score}% Overlap** |",
            f"| **Transition Difficulty** | {diff} |",
            f"| **Estimated Pivot Timeline** | ⏱️ {timeline} |",
            "",
            f"### ✅ Directly Transferable Skills (100% Match)",
            *[f"  • {s}" for s in shared],
            "",
            f"### 🌉 Bridge Skills (Adapt & Recontextualize)",
            *[f"  • {b}" for b in bridge],
            "",
            f"### 🎯 Delta Skills to Acquire (The Gap)",
            *[f"  • {d}" for d in delta],
            "",
            f"### 🎓 Recommended Bridge Certifications",
            f"  {', '.join(certs)}",
            "",
            f"### 🛡️ Breaking Into Cybersecurity Mentorship Note",
            f"> *\"{advice}\"*",
            "",
        ])
    else:
        # Generic heuristic comparison if direct matrix entry not explicitly pre-computed
        src_skills = set(sum(src_data.get("skills_mindmap", {}).values(), []))
        tgt_skills = set(sum(tgt_data.get("skills_mindmap", {}).values(), []))

        lines.extend([
            f"### 🔍 Skills Intersection Analysis",
            f"- **Your Source Strengths ({src_title})**: {len(src_skills)} identified foundation areas.",
            f"- **Target Requirements ({tgt_title})**: {len(tgt_skills)} core domains.",
            "",
            f"### 🎓 Recommended First Steps",
            f"1. Audit target job postings for {tgt_title} in your area.",
            f"2. Build hands-on lab projects to cover the {tgt_title} tooling.",
            f"3. Target relevant foundational certs: {', '.join(tgt_data.get('certs_mindmap', {}).get('core', ['Security+']))}.",
        ])

    return "\n".join(lines)
