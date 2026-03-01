#!/usr/bin/env python3
"""
SITE CONTENT SYNTHESIZER
========================

"Local NotebookLM" — Scans ~/Documents to produce structured JSON
for David Kirsh's personal academic website.

Three modules:
1. CV Parser: Extracts publications, grants, talks from the .docx CV
2. Directory Classifier: Sorts 373 folders into project vs admin
3. Project Summarizer: Reads key documents per project, generates
   short_abstract + long_summary + key_findings

Usage:
    python scripts/site_content_synthesizer.py --parse-cv         # Step 1
    python scripts/site_content_synthesizer.py --classify-dirs    # Step 2
    python scripts/site_content_synthesizer.py --status           # Show progress

Author: AG (Website Sprint)
Date: 2026-02-25
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ── Paths ──
DOCS_ROOT = Path("/Users/davidusa/Documents")
CV_PATH = DOCS_ROOT / "CV" / "__Kirsh_2025_Acad_CV_Full" / " __Kirsh_2025_Jan-Acad_CV_full.docx"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "website"
PUBLICATIONS_DIR = DOCS_ROOT / "PUBLICATIONS"

# ── Administrative folder patterns (not projects) ──
ADMIN_PATTERNS = {
    "1Password", "ATT FIber Plan", "AutoSave Word", "Budgets", "CAR+new BMW",
    "Groupons etc", "HEALTH - ME", "__HEALTH_mine", "Household Expenses",
    "Laguna Beach", "Microwave", "Money", "Passover", "Pond", "Purchase_research",
    "Purchases", "Receipts", "Recipe", "FOOD - RECIPES", "Food_Yvonne",
    "Cooking_Recipe_Project", "Refinance 2016", "Retirement", "Sauna",
    "SSD Setup Software", "Stocks", "Tax Audit", "Taxes", "Temp", "Travel",
    "US Citizenship", "Vaccine", "Water Purifier", "WebEx", "Zoom",
    "_AutoRecover Word", "__purchase_returns", "serial licenses etc",
    "Fireplace", "Breakfast Nook", "Furniture", "GARDEN", "Soap Dispenser",
    "Exercise", "Meeno's room redesign", "Will and Estate - Nirvana Planning",
    "Will and Testimont", "Yom Kippur", "23 and Me", "Breast Cancer",
    "Heart Research Stuff", "Food Health", "Polish Passport", "Poland passport",
    "New Financial Analysis 2018", "Scans", "_Screenshots", "Screenshots",
    "Vuze Downloads", "Downie Vid Capture", "Movies", "Music_Sheet",
    "Invitations", "Friends", "Kids", "Milo", "JOHN", "Josephine", "Joy",
    "Red Arrows", "Self Improvement", "Routines", "Hints",
    "House Remodel 1", "2116 Merida", "2116 Merida HOUSE",
    "Acephate 97UP Insecticide", "WoodWorking", "PET vs SPECT",
    "Adobe", "MATLAB", "Miscellaneous", "Temp", "POOJAH",
}

# ── Project classification keywords ──
ACADEMIC_KEYWORDS = {
    "cognition", "cognitive", "embodied", "enactive", "extended", "distributed",
    "creativity", "creative", "design", "architecture", "neuro", "neural",
    "perception", "attention", "memory", "learning", "interactivity",
    "interactive", "thinking", "thought", "gesture", "dance", "movement",
    "visualization", "visual", "robotics", "robot", "ai", "llm",
    "experiment", "study", "research", "theory", "phenomenology",
    "affordance", "predictive", "coding", "fractal", "goldilocks",
    "legibility", "wayfinding", "space", "spatial", "haptic",
    "tangible", "computing", "projection", "interface", "hci", "chi",
    "cogsci", "emotion", "stress", "wellbeing", "biophilia",
    "book", "article", "paper", "publication", "proposal", "grant",
    "lab", "vr", "xr", "metaverse",
}


def docx_to_text(path: Path) -> str:
    """Convert .docx to plain text using macOS textutil."""
    result = subprocess.run(
        ["textutil", "-convert", "txt", str(path), "-stdout"],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout


# ═══════════════════════════════════════════════════════
# MODULE 1: CV PARSER
# ═══════════════════════════════════════════════════════

def parse_cv() -> dict:
    """Parse the CV .docx into structured sections."""
    print("═" * 60)
    print("  CV PARSER")
    print("═" * 60)

    text = docx_to_text(CV_PATH)
    if not text:
        print("❌ Could not read CV")
        return {}

    lines = text.split("\n")
    print(f"  Read {len(lines)} lines from CV")

    result = {
        "name": "David Kirsh",
        "title": "Professor",
        "department": "Department of Cognitive Science",
        "university": "University of California, San Diego",
        "email": "kirsh@ucsd.edu",
        "website": "http://adrenaline.ucsd.edu/kirsh",
        "research_interests": "",
        "education": [],
        "employment": [],
        "awards": [],
        "grants": [],
        "publications": [],
        "invited_talks": [],
        "teaching": [],
    }

    # Extract research interests
    for i, line in enumerate(lines):
        if "Research Interests:" in line:
            interests = line.split("Research Interests:")[-1].strip()
            # May continue on next line
            if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip().startswith(("Education", "Employment")):
                interests += " " + lines[i + 1].strip()
            result["research_interests"] = interests.strip()
            break

    # Extract publications
    publications = _extract_publications(lines)
    result["publications"] = publications
    print(f"  Found {len(publications)} publications")

    # Extract education
    result["education"] = _extract_education(lines)
    print(f"  Found {len(result['education'])} education entries")

    # Extract employment
    result["employment"] = _extract_employment(lines)
    print(f"  Found {len(result['employment'])} employment entries")

    # Extract awards
    result["awards"] = _extract_section_bullets(lines, "Awards & Honors:", [
        "Major Grants", "Publications", "Employment"
    ])
    print(f"  Found {len(result['awards'])} awards")

    # Extract grants
    result["grants"] = _extract_section_bullets(lines, "Major Grants", [
        "Publications", "Books", "Teaching", "Invited"
    ])
    print(f"  Found {len(result['grants'])} grants")

    # Extract invited talks
    result["invited_talks"] = _extract_talks(lines)
    print(f"  Found {len(result['invited_talks'])} invited talks")

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "cv_parsed.json"
    out_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"\n  ✅ Saved to {out_path}")

    return result


def _extract_publications(lines: list[str]) -> list[dict]:
    """Extract publications from CV text."""
    pubs = []
    in_pubs = False
    current_section = ""

    for line in lines:
        stripped = line.strip()

        # Detect publication sections
        if any(h in stripped for h in [
            "Refereed Journal Articles",
            "Books Authored",
            "Book Chapters",
            "Refereed Conference Papers",
            "Working Papers",
            "Reports",
        ]):
            in_pubs = True
            current_section = stripped.rstrip(":")
            continue

        # End of publications
        if in_pubs and any(h in stripped for h in [
            "Invited Talks", "Invited Lecture", "Teaching", "Service",
            "Students Supervised", "PhD Students",
        ]):
            in_pubs = False
            continue

        if not in_pubs or not stripped:
            continue

        # Try to parse a publication entry
        # Common formats:
        #   Kirsh, D. (2009). Title. Venue, Vol, Pages.
        #   Kirsh, D. & Author, B. (2010). Title. In Proc...
        pub_match = re.match(
            r'^(?:(?:\d+\.?\s+)|•\s+)?(.+?)\((\d{4})\)\.\s*(.+)',
            stripped
        )
        if pub_match:
            authors = pub_match.group(1).strip().rstrip(",").rstrip(".")
            year = int(pub_match.group(2))
            rest = pub_match.group(3).strip()

            # Split title from venue at the first period after reasonable length
            title = rest
            venue = ""
            # Look for pattern: Title. Venue...
            title_split = re.split(r'\.\s+(?=[A-Z])', rest, maxsplit=1)
            if len(title_split) == 2 and len(title_split[0]) > 10:
                title = title_split[0]
                venue = title_split[1]

            pubs.append({
                "authors": authors,
                "year": year,
                "title": title,
                "venue": venue,
                "section": current_section,
                "raw": stripped,
            })
        elif stripped and in_pubs and len(stripped) > 30:
            # Fallback: just record the raw line
            # Try year extraction
            year_match = re.search(r'\((\d{4})\)', stripped)
            year = int(year_match.group(1)) if year_match else None
            pubs.append({
                "authors": "",
                "year": year,
                "title": stripped[:100],
                "venue": "",
                "section": current_section,
                "raw": stripped,
            })

    return pubs


def _extract_education(lines: list[str]) -> list[dict]:
    """Extract education entries."""
    entries = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if "Education:" in stripped:
            in_section = True
            continue
        if in_section and any(h in stripped for h in ["Employment:", "Awards"]):
            break
        if in_section and stripped:
            # Pattern: 1984-87  Post-Doctoral Fellow, AI Lab, MIT
            match = re.match(r'(\d{4}[-–]\d{2,4})\s+(.*)', stripped)
            if match:
                entries.append({
                    "years": match.group(1),
                    "description": match.group(2).strip()
                })
    return entries


def _extract_employment(lines: list[str]) -> list[dict]:
    """Extract employment entries."""
    entries = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped == "Employment:":
            in_section = True
            continue
        if in_section and any(h in stripped for h in ["Awards", "Major Grants", "Publications"]):
            break
        if in_section and stripped:
            match = re.match(r'(\d{4}[-–\s]*\d{0,4})\s+(.*)', stripped)
            if match:
                entries.append({
                    "years": match.group(1).strip(),
                    "description": match.group(2).strip()
                })
    return entries


def _extract_section_bullets(lines: list[str], start_marker: str,
                              end_markers: list[str]) -> list[str]:
    """Extract bullet items from a named section."""
    items = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if start_marker in stripped:
            in_section = True
            continue
        if in_section and any(m in stripped for m in end_markers):
            break
        if in_section and stripped and len(stripped) > 5:
            items.append(stripped.lstrip("•").lstrip("·").strip())
    return items


def _extract_talks(lines: list[str]) -> list[dict]:
    """Extract invited talks with year grouping."""
    talks = []
    in_section = False
    current_year = None

    for line in lines:
        stripped = line.strip()

        if any(h in stripped for h in ["Invited Talks", "Keynotes", "Invited Speaker"]):
            in_section = True
            continue
        if in_section and any(h in stripped for h in [
            "Teaching", "Service", "Students", "PhD Students",
            "Invited Lecture series"
        ]):
            if "Lecture series" not in stripped:
                break

        if not in_section:
            continue

        # Year header
        year_match = re.match(r'^(\d{4})\s*$', stripped)
        if year_match:
            current_year = int(year_match.group(1))
            continue

        if stripped.startswith("•") and current_year:
            talk_text = stripped.lstrip("•").strip()
            talks.append({
                "year": current_year,
                "description": talk_text,
            })

    return talks


# ═══════════════════════════════════════════════════════
# MODULE 2: DIRECTORY CLASSIFIER
# ═══════════════════════════════════════════════════════

def classify_directories() -> dict:
    """Classify ~/Documents subdirectories into projects vs administrative."""
    print("═" * 60)
    print("  DIRECTORY CLASSIFIER")
    print("═" * 60)

    projects = []
    admin = []
    courses = []
    conferences = []
    people = []
    personal = []

    for entry in sorted(DOCS_ROOT.iterdir()):
        if not entry.is_dir():
            continue

        name = entry.name
        name_lower = name.lower()

        # Skip hidden
        if name.startswith("."):
            continue

        # Check admin list
        if name in ADMIN_PATTERNS:
            admin.append({"name": name, "category": "administrative"})
            continue

        # Classify by pattern
        category = _classify_dir(name, name_lower, entry)

        if category == "course":
            courses.append({"name": name, "path": str(entry)})
        elif category == "conference":
            conferences.append({"name": name, "path": str(entry)})
        elif category == "person":
            people.append({"name": name, "path": str(entry)})
        elif category == "personal":
            personal.append({"name": name, "category": "personal"})
        elif category == "project":
            # Count files and get file types
            file_count = 0
            doc_count = 0
            image_count = 0
            for f in entry.rglob("*"):
                if f.is_file():
                    file_count += 1
                    ext = f.suffix.lower()
                    if ext in (".pdf", ".doc", ".docx", ".md", ".txt", ".pptx"):
                        doc_count += 1
                    elif ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov"):
                        image_count += 1
                    if file_count > 500:
                        break  # Don't scan massive dirs

            projects.append({
                "name": name,
                "path": str(entry),
                "file_count": min(file_count, 500),
                "doc_count": doc_count,
                "image_count": image_count,
                "relevance": _score_project_relevance(name),
            })
        else:
            admin.append({"name": name, "category": "uncategorized"})

    # Sort projects by relevance
    projects.sort(key=lambda p: -p.get("relevance", 0))

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_dirs": len(projects) + len(admin) + len(courses) + len(conferences) + len(people) + len(personal),
        "projects": projects,
        "courses": courses,
        "conferences": conferences,
        "people": people,
        "admin": admin,
        "personal": personal,
        "summary": {
            "projects": len(projects),
            "courses": len(courses),
            "conferences": len(conferences),
            "people": len(people),
            "admin": len(admin),
            "personal": len(personal),
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "directory_classification.json"
    out_path.write_text(json.dumps(result, indent=2))

    print(f"\n  Classification results:")
    for cat, count in result["summary"].items():
        print(f"    {cat:15s}: {count:3d}")
    print(f"\n  Top 15 projects by relevance:")
    for p in projects[:15]:
        print(f"    [{p['relevance']:4.1f}] {p['name'][:50]:50s} ({p['doc_count']} docs, {p['image_count']} imgs)")
    print(f"\n  ✅ Saved to {out_path}")

    return result


def _classify_dir(name: str, name_lower: str, path: Path) -> str:
    """Classify a single directory."""
    # Course patterns
    if re.match(r'^(Cogs?\s*\d|__?\d{3}|__?199|102A|187[AB]|260)', name):
        return "course"
    if "cogs" in name_lower and any(c.isdigit() for c in name):
        return "course"

    # Conference patterns
    if re.match(r'^(Chi\d|Cogsci\s+\d|EuroCogsci|MOCO|CILC)', name, re.IGNORECASE):
        return "conference"
    if any(w in name_lower for w in ["conference", "workshop", "symposium", "festival"]):
        return "conference"

    # Location/travel
    if name in {"Australia", "Barcelona - 2024", "Bellagio", "Berlin",
                "Cambridge 2006", "Denmark", "Helsinki_2019", "Nice_Bernard_2019",
                "Paris_MOCO", "Pescara 2024 ", "Poland", "Purdue",
                "Wellness Barcelona"}:
        return "conference"  # Likely conference travel

    # People
    if name in {"Abel", "Adam Mekrut", "Amy Fox", "Andrea", "Andrea_Chiba",
                "Aslan", "Bob Sharf", "From Joachim", "Gaudillet",
                "Jean Mandler", "Larry Muhlstein", "Linda Kaastra", "Manny",
                "Matt Fain", "Maya", "Michael Allen", "Michal",
                "Natalie Sleiman - Omar Fayed", "Sam Sandwiess", "Sergei",
                "daniel smithwick", "arturs arthur"}:
        return "person"

    # Personal/house
    if any(w in name_lower for w in ["house", "merida", "personal", "passport"]):
        return "personal"

    # Academic project detection
    academic_score = 0
    for keyword in ACADEMIC_KEYWORDS:
        if keyword in name_lower:
            academic_score += 1

    # Strong project signals
    if name in {"DK Website", "DK Website alias", "PRESENTATIONS", "PUBLICATIONS",
                "CV", "Lab", "VR Lab", "XR LAB and Courses", "Design Lab",
                "REPO", "Article_Eater_Repo", "GitHub"}:
        return "project"

    if academic_score >= 1:
        return "project"

    # Folders starting with __ are often important project folders
    if name.startswith("__") and not name.startswith("___"):
        return "project"

    # Year folders
    if re.match(r'^\d{4}$', name):
        return "personal"

    return "project"  # Default to project to be inclusive


def _score_project_relevance(name: str) -> float:
    """Score how relevant a project folder is for the website."""
    name_lower = name.lower()
    score = 0

    # Core research topics get highest scores
    core_topics = {
        "embodied cognition": 5, "distributed cognition": 5,
        "interactivity": 5, "creativity": 5, "architecture": 5,
        "neuroarchitecture": 5, "design": 4, "thinking": 4,
        "extended mind": 5, "enactive": 4, "predictive coding": 4,
        "gesture": 4, "dance": 4, "vr lab": 5, "xr": 4,
        "biophilia": 4, "affordance": 4, "legibility": 3,
        "smart cities": 3, "robotics": 3, "ai": 3,
        "book": 4, "publication": 5, "presentation": 4,
        "lab": 5, "Grant": 3, "proposal": 3,
    }
    for topic, weight in core_topics.items():
        if topic in name_lower:
            score += weight

    # Named collaborations/labs
    if any(w in name for w in ["ANFA", "BARTLETT", "UCL", "Wellcome", "IBM",
                                "Disney", "Steelcase", "Darpa", "KAVLI", "AUTODESK"]):
        score += 3

    return score


# ═══════════════════════════════════════════════════════
# MODULE 3: STATUS
# ═══════════════════════════════════════════════════════

def show_status():
    """Show current pipeline status."""
    print("═" * 60)
    print("  SITE CONTENT SYNTHESIZER STATUS")
    print("═" * 60)

    cv_path = OUTPUT_DIR / "cv_parsed.json"
    if cv_path.exists():
        data = json.loads(cv_path.read_text())
        print(f"\n  ✅ CV parsed:")
        print(f"     Publications: {len(data.get('publications', []))}")
        print(f"     Awards: {len(data.get('awards', []))}")
        print(f"     Grants: {len(data.get('grants', []))}")
        print(f"     Talks: {len(data.get('invited_talks', []))}")
        print(f"     Education: {len(data.get('education', []))}")
    else:
        print(f"\n  ❌ CV not yet parsed (run --parse-cv)")

    dir_path = OUTPUT_DIR / "directory_classification.json"
    if dir_path.exists():
        data = json.loads(dir_path.read_text())
        summary = data.get("summary", {})
        print(f"\n  ✅ Directories classified:")
        for cat, count in summary.items():
            print(f"     {cat}: {count}")
    else:
        print(f"\n  ❌ Directories not classified (run --classify-dirs)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Site content synthesizer")
    parser.add_argument("--parse-cv", action="store_true", help="Parse CV into structured JSON")
    parser.add_argument("--classify-dirs", action="store_true", help="Classify ~/Documents directories")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    parser.add_argument("--status", action="store_true", help="Show status")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.parse_cv or args.all:
        parse_cv()
        if args.all:
            classify_directories()
    elif args.classify_dirs:
        classify_directories()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
