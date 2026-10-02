import os
import sys
import re
import pymupdf


# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")

sys.path.insert(0, BACKEND)

from database import get_connection


# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------

def extract_text(pdf_path):
    text = ""

    doc = pymupdf.open(pdf_path)

    for page in doc:
        text += page.get_text()

    doc.close()

    return text.strip()


# --------------------------------------------------
# NAME EXTRACTION
# --------------------------------------------------

def extract_name(text):
    lines = text.splitlines()

    for line in lines[:10]:

        line = line.strip()

        if not line:
            continue

        # Skip email
        if "@" in line:
            continue

        # Skip phone numbers
        if re.search(r"\d{5,}", line):
            continue

        # Skip links
        if "linkedin" in line.lower():
            continue

        if "github" in line.lower():
            continue

        # Skip common headings
        headings = [
            "resume",
            "curriculum vitae",
            "cv",
            "career objective",
            "objective"
        ]

        if line.lower() in headings:
            continue

        # Name should normally be short
        if len(line.split()) <= 6:
            return line

    return ""


# --------------------------------------------------
# EMAIL EXTRACTION
# --------------------------------------------------

def extract_email(text):

    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    if match:
        return match.group(0)

    return ""


# --------------------------------------------------
# PHONE EXTRACTION
# --------------------------------------------------

def extract_phone(text):

    match = re.search(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text
    )

    if match:
        return match.group(0)

    return ""


# --------------------------------------------------
# SKILL EXTRACTION
# --------------------------------------------------

SKILLS = [
    "python",
    "java",
    "c++",
    "c",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",

    "html",
    "css",
    "javascript",
    "typescript",
    "react",
    "react.js",
    "node.js",

    "fastapi",
    "flask",
    "django",
    "rest api",
    "rest apis",

    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",

    "natural language processing",
    "computer vision",

    "tensorflow",
    "pytorch",
    "scikit-learn",

    "pandas",
    "numpy",

    "llm",
    "llms",
    "rag",
    "generative ai",

    "mcp",

    "git",
    "github",

    "docker",
    "aws",
    "azure"
]


def extract_skills(text):

    text_lower = text.lower()

    found_skills = []

    for skill in SKILLS:

        # Convert . into literal dot for regex
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text_lower):

            skill_name = skill

            # Normalize names
            if skill_name == "llms":
                skill_name = "llm"

            if skill_name == "react.js":
                skill_name = "react"

            if skill_name == "rest apis":
                skill_name = "rest api"

            if skill_name not in found_skills:
                found_skills.append(skill_name)

    return found_skills


# --------------------------------------------------
# SECTION EXTRACTION
# --------------------------------------------------

def extract_section(text, section_names):

    lines = text.splitlines()

    inside_section = False
    section_lines = []

    for line in lines:

        clean_line = line.strip()

        if not clean_line:
            continue

        lower_line = clean_line.lower()

        # Check whether this is the section we want
        if any(
            lower_line == section.lower()
            for section in section_names
        ):
            inside_section = True
            continue

        if inside_section:

            # Detect another major section
            major_sections = [
                "education",
                "technical skills",
                "skills",
                "experience",
                "work experience",
                "professional experience",
                "projects",
                "certifications",
                "achievements",
                "strengths",
                "summary",
                "career objective",
                "objective",
                "languages",
                "interests"
            ]

            if lower_line in major_sections:
                break

            section_lines.append(clean_line)

    return " | ".join(section_lines)


# --------------------------------------------------
# EXPERIENCE EXTRACTION
# --------------------------------------------------

def extract_experience(text):

    experience_sections = [
        "experience",
        "work experience",
        "professional experience",
        "internship",
        "internships"
    ]

    return extract_section(text, experience_sections)


# --------------------------------------------------
# EDUCATION EXTRACTION
# --------------------------------------------------

def extract_education(text):

    education_sections = [
        "education",
        "academic background",
        "educational background"
    ]

    return extract_section(text, education_sections)


# --------------------------------------------------
# PROJECT EXTRACTION
# --------------------------------------------------

def extract_projects(text):

    project_sections = [
        "projects",
        "academic projects",
        "personal projects",
        "projects & internships"
    ]

    return extract_section(text, project_sections)


# --------------------------------------------------
# PROCESS ONE RESUME
# --------------------------------------------------

def process_resume(resume):

    resume_id = resume["id"]
    job_id = resume["job_id"]
    filename = resume["filename"]

    print("----------------------------------------")
    print(f"Processing Resume ID: {resume_id}")
    print(f"File: {filename}")

    # Resume location
    upload_dir = os.path.join(
        BACKEND,
        "uploads",
        job_id
    )

    file_path = os.path.join(
        upload_dir,
        filename
    )

    # Check file
    if not os.path.exists(file_path):

        print("ERROR: Resume file not found")

        conn = get_connection()

        conn.execute(
            """
            UPDATE resumes
            SET status = ?,
                processing_stage = ?
            WHERE id = ?
            """,
            ("Failed", "Failed", resume_id)
        )

        conn.commit()
        conn.close()

        return

    conn = get_connection()

    try:

        # Mark as currently processing
        conn.execute(
            """
            UPDATE resumes
            SET status = ?,
                processing_stage = ?
            WHERE id = ?
            """,
            ("Extracting", "Extracting", resume_id)
        )

        conn.commit()

        # ------------------------------------------
        # EXTRACT PDF TEXT
        # ------------------------------------------

        text = extract_text(file_path)

        if not text:

            raise Exception("No text could be extracted from PDF")

        # ------------------------------------------
        # EXTRACT CANDIDATE DETAILS
        # ------------------------------------------

        name = extract_name(text)

        email = extract_email(text)

        phone = extract_phone(text)

        skills = extract_skills(text)

        experience = extract_experience(text)

        education = extract_education(text)

        projects = extract_projects(text)

        # ------------------------------------------
        # SAVE DATA
        # ------------------------------------------

        conn.execute(
            """
            UPDATE resumes
            SET
                status = ?,
                processing_stage = ?,
                extracted_text = ?,
                name = ?,
                email = ?,
                phone = ?,
                skills = ?,
                experience = ?,
                education = ?,
                projects = ?,
                score = NULL,
                matched_skills = NULL,
                missing_skills = NULL
            WHERE id = ?
            """,
            (
                "Extracted",
                "Extracted",
                text,
                name,
                email,
                phone,
                ", ".join(skills),
                experience,
                education,
                projects,
                resume_id
            )
        )

        conn.commit()

        print("Extraction successful")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Phone: {phone}")
        print(f"Skills: {skills}")

    except Exception as e:

        print(f"ERROR: {e}")

        conn.execute(
            """
            UPDATE resumes
            SET
                status = ?,
                processing_stage = ?
            WHERE id = ?
            """,
            ("Failed", "Failed", resume_id)
        )

        conn.commit()

    finally:

        conn.close()


# --------------------------------------------------
# MAIN WORKER
# --------------------------------------------------

def main():

    conn = get_connection()

    resumes = conn.execute(
        """
        SELECT id, job_id, filename
        FROM resumes
        WHERE processing_stage = 'Queued'
        ORDER BY id
        """
    ).fetchall()

    conn.close()

    if not resumes:

        print("No queued resumes found.")
        return

    print(f"Found {len(resumes)} queued resume(s).")

    for resume in resumes:

        process_resume(resume)

    print("----------------------------------------")
    print("Extraction worker finished.")


# --------------------------------------------------
# START
# --------------------------------------------------

if __name__ == "__main__":
    main()