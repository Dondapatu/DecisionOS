import os
import sys
import re
import pymupdf
from ai_scorer import calculate_score

# -----------------------------
# Project Paths
# -----------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")

sys.path.insert(0, BACKEND)

from database import get_connection

# -----------------------------
# Skill Dictionary
# -----------------------------
SKILL_LIST = [
    "python",
    "java",
    "c",
    "c++",
    "sql",
    "react",
    "react.js",
    "fastapi",
    "flask",
    "django",
    "rest",
    "machine learning",
    "deep learning",
    "rag",
    "llm",
    "llms",
    "nlp",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",
    "mongodb",
    "mysql",
    "aws",
    "jwt",
    "oauth",
    "git",
    "yolo",
    "ocr"
]

# -----------------------------
# PDF Text Extraction
# -----------------------------
def extract_text(pdf_path):
    text = ""

    doc = pymupdf.open(pdf_path)

    for page in doc:
        text += page.get_text()

    doc.close()

    return text

# -----------------------------
# Candidate Information
# -----------------------------
def find_email(text):
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )
    return match.group(0) if match else ""


def find_phone(text):
    match = re.search(r"(\+91[\s-]?)?[6-9]\d{9}", text)
    return match.group(0) if match else ""


def find_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines[:5]:
        if "resume" not in line.lower() and len(line.split()) <= 4:
            return line

    return ""


def find_skills(text):
    text_lower = text.lower()
    found = []

    for skill in SKILL_LIST:
        if skill in text_lower:
            found.append(skill.title())

    return ", ".join(found)

# -----------------------------
# Section Extraction
# -----------------------------
def find_section(text, keywords):
    headings = [
        "education",
        "experience",
        "projects",
        "skills",
        "technical skills",
        "certifications",
        "strengths",
        "professional skills"
    ]

    lines = text.splitlines()

    collecting = False
    result = []

    for line in lines:

        lower = line.lower().strip()

        if any(k in lower for k in keywords):
            collecting = True
            continue

        if collecting:

            if any(h in lower for h in headings):
                break

            if line.strip():
                result.append(line.strip())

    return " | ".join(result[:12])

# -----------------------------
# Main Worker
# -----------------------------
def process_resumes():

    conn = get_connection()

    resumes = conn.execute("""
        SELECT id, job_id, filename
        FROM resumes
        WHERE status='Queued'
    """).fetchall()

    if not resumes:
        print("No queued resumes found.")
        conn.close()
        return

    for resume in resumes:

        pdf_path = os.path.join(
            BACKEND,
            "uploads",
            resume["job_id"],
            resume["filename"]
        )

        if not os.path.exists(pdf_path):
            print(f"Missing: {resume['filename']}")
            continue

        # Extract text
        text = extract_text(pdf_path)

        # Get job skills
        job = conn.execute(
            "SELECT skills FROM jobs WHERE id=?",
            (resume["job_id"],)
        ).fetchone()

        job_skills = job["skills"] if job else ""

        # AI Match Score
        score, matched, missing = calculate_score(
            job_skills,
            text
        )

        # Save everything
        conn.execute("""
            UPDATE resumes
            SET
                extracted_text=?,
                name=?,
                email=?,
                phone=?,
                skills=?,
                experience=?,
                education=?,
                projects=?,
                score=?,
                status='Extracted'
            WHERE id=?
        """, (
            text,
            find_name(text),
            find_email(text),
            find_phone(text),
            find_skills(text),
            find_section(text, ["experience"]),
            find_section(text, ["education"]),
            find_section(text, ["projects", "project"]),
            score,
            resume["id"]
        ))

        print(f"Extracted: {resume['filename']}")
        print(f"AI Score: {score}")
        print(f"Matched Skills: {matched}")
        print(f"Missing Skills: {missing}")
        print("-" * 40)

    conn.commit()
    conn.close()

    print("All queued resumes processed.")

# -----------------------------
# Run Worker
# -----------------------------
if __name__ == "__main__":
    process_resumes()