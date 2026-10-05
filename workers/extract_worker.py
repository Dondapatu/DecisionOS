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
# DOCUMENT VALIDATION
# --------------------------------------------------

RESUME_SECTIONS = [
    "resume",
    "curriculum vitae",
    "cv",
    "summary",
    "professional summary",
    "career objective",
    "objective",
    "experience",
    "work experience",
    "professional experience",
    "internship",
    "internships",
    "education",
    "academic background",
    "educational background",
    "skills",
    "technical skills",
    "projects",
    "academic projects",
    "personal projects",
    "certifications",
    "achievements"
]


NON_RESUME_KEYWORDS = [
    "interview task",
    "assignment",
    "coding task",
    "take home assignment",
    "technical task",
    "evaluation criteria",
    "deliverables",
    "submission requirements",
    "problem statement",
    "dataset",
    "train the model",
    "model training",
    "text generation task",
    "implementation task",
    "task instructions"
]


def validate_document(text):

    if not text:
        return False, "Unknown", "No text could be extracted"

    text_lower = text.lower()

    # ----------------------------------------------
    # Resume signals
    # ----------------------------------------------

    resume_signal_count = 0

    # Email
    if re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    ):
        resume_signal_count += 1

    # Indian phone number
    if re.search(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text
    ):
        resume_signal_count += 1

    # Common resume sections
    section_matches = 0

    for section in RESUME_SECTIONS:

        pattern = r"\b" + re.escape(section) + r"\b"

        if re.search(pattern, text_lower):
            section_matches += 1

    if section_matches >= 2:
        resume_signal_count += 2

    elif section_matches == 1:
        resume_signal_count += 1

    # Technical skills
    technical_keywords = [
        "python",
        "java",
        "sql",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "data science",
        "react",
        "javascript",
        "fastapi",
        "flask",
        "django",
        "tensorflow",
        "pytorch",
        "pandas",
        "numpy",
        "llm",
        "rag"
    ]

    technical_matches = 0

    for keyword in technical_keywords:

        if keyword in text_lower:
            technical_matches += 1

    if technical_matches >= 3:
        resume_signal_count += 1

    # ----------------------------------------------
    # Non-resume signals
    # ----------------------------------------------

    non_resume_matches = []

    for keyword in NON_RESUME_KEYWORDS:

        if keyword in text_lower:
            non_resume_matches.append(keyword)

    # ----------------------------------------------
    # Strong non-resume document
    # ----------------------------------------------

    # If the document contains several task/assignment
    # signals and does not have enough resume structure,
    # classify it as a non-resume.

    if (
        len(non_resume_matches) >= 2
        and section_matches < 3
        and resume_signal_count < 4
    ):

        reason = (
            "Document appears to be an assignment, "
            "interview task, or technical task rather than a resume."
        )

        return False, "Non-Resume", reason

    # ----------------------------------------------
    # Resume decision
    # ----------------------------------------------

    if resume_signal_count >= 3:

        return True, "Resume", "Resume structure detected"

    # ----------------------------------------------
    # Possible resume with weak structure
    # ----------------------------------------------

    # Some resumes may not contain phone numbers,
    # emails, or standard headings. Allow documents
    # with enough technical/resume-related evidence.

    if (
        section_matches >= 2
        or technical_matches >= 3
    ):

        return True, "Resume", "Resume-related content detected"

    # ----------------------------------------------
    # Invalid document
    # ----------------------------------------------

    return (
        False,
        "Non-Resume",
        "Document does not contain enough resume-related information"
    )


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

    # ------------------------------------------
    # CHECK FILE
    # ------------------------------------------

    if not os.path.exists(file_path):

        print("ERROR: Resume file not found")

        conn = get_connection()

        conn.execute(
            """
            UPDATE resumes
            SET
                status = ?,
                processing_stage = ?,
                validation_status = ?,
                validation_reason = ?
            WHERE id = ?
            """,
            (
                "Failed",
                "Failed",
                "Invalid",
                "Resume file not found",
                resume_id
            )
        )

        conn.commit()
        conn.close()

        return

    conn = get_connection()

    try:

        # ------------------------------------------
        # MARK AS CURRENTLY PROCESSING
        # ------------------------------------------

        conn.execute(
            """
            UPDATE resumes
            SET
                status = ?,
                processing_stage = ?
            WHERE id = ?
            """,
            (
                "Extracting",
                "Extracting",
                resume_id
            )
        )

        conn.commit()

        # ------------------------------------------
        # EXTRACT PDF TEXT
        # ------------------------------------------

        text = extract_text(file_path)

        if not text:

            raise Exception(
                "No text could be extracted from PDF"
            )

        # ------------------------------------------
        # VALIDATE DOCUMENT
        # ------------------------------------------

        is_resume, document_type, validation_reason = (
            validate_document(text)
        )

        print(f"Document Type: {document_type}")
        print(f"Validation: {validation_reason}")

        # ------------------------------------------
        # NON-RESUME
        # ------------------------------------------

        if not is_resume:

            conn.execute(
                """
                UPDATE resumes
                SET
                    status = ?,
                    processing_stage = ?,
                    extracted_text = ?,
                    document_type = ?,
                    validation_status = ?,
                    validation_reason = ?,
                    score = NULL,
                    matched_skills = NULL,
                    missing_skills = NULL,
                    ai_recommendation = NULL
                WHERE id = ?
                """,
                (
                    "Excluded",
                    "Excluded",
                    text,
                    document_type,
                    "Invalid",
                    validation_reason,
                    resume_id
                )
            )

            conn.commit()

            print("Document excluded from AI scoring.")
            print("----------------------------------------")

            return

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
        # SAVE VALID RESUME
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
                document_type = ?,
                validation_status = ?,
                validation_reason = ?,
                score = NULL,
                matched_skills = NULL,
                missing_skills = NULL,
                ai_recommendation = NULL
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
                document_type,
                "Valid",
                validation_reason,
                resume_id
            )
        )

        conn.commit()

        print("Resume validation successful")
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
                processing_stage = ?,
                validation_status = ?,
                validation_reason = ?
            WHERE id = ?
            """,
            (
                "Failed",
                "Failed",
                "Invalid",
                str(e),
                resume_id
            )
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
    print("Extraction and validation worker finished.")


# --------------------------------------------------
# START
# --------------------------------------------------

if __name__ == "__main__":
    main()