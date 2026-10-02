import os
import sys
import re


# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")

sys.path.insert(0, BACKEND)

from database import get_connection


# --------------------------------------------------
# DOCUMENT TYPES THAT ARE NOT RESUMES
# --------------------------------------------------

INVALID_DOCUMENTS = {
    "statement of purpose": "Statement of Purpose",
    "sop": "Statement of Purpose",
    "cover letter": "Cover Letter",
    "recommendation letter": "Recommendation Letter",
    "letter of recommendation": "Recommendation Letter",
    "motivation letter": "Motivation Letter",
    "transcript": "Academic Transcript",
    "marksheet": "Marksheet",
    "mark sheet": "Marksheet",
    "certificate": "Certificate"
}


# --------------------------------------------------
# RESUME SECTION INDICATORS
# --------------------------------------------------

RESUME_SECTIONS = [
    "education",
    "technical skills",
    "skills",
    "experience",
    "work experience",
    "professional experience",
    "projects",
    "certifications",
    "achievements",
    "internship",
    "internships",
    "career objective",
    "objective",
    "professional summary",
    "summary"
]


# --------------------------------------------------
# CHECK STRONG INVALID DOCUMENT
# --------------------------------------------------

def detect_invalid_document(text):

    lines = [
        line.strip().lower()
        for line in text.splitlines()
        if line.strip()
    ]

    # Only inspect the beginning of the document.
    # This prevents words such as "certificate"
    # inside a resume from causing false detection.

    first_lines = lines[:10]

    for line in first_lines:

        for keyword, document_type in INVALID_DOCUMENTS.items():

            if line == keyword:
                return document_type

            # Example:
            # Statement of Purpose - ABC University
            if line.startswith(keyword + " "):
                return document_type

            if line.startswith(keyword + ":"):
                return document_type

            if line.startswith(keyword + "-"):
                return document_type

    return None


# --------------------------------------------------
# CHECK RESUME STRUCTURE
# --------------------------------------------------

def count_resume_sections(text):

    lower_text = text.lower()

    count = 0
    found_sections = []

    for section in RESUME_SECTIONS:

        pattern = r"\b" + re.escape(section) + r"\b"

        if re.search(pattern, lower_text):

            count += 1
            found_sections.append(section)

    return count, found_sections


# --------------------------------------------------
# VALIDATE DOCUMENT
# --------------------------------------------------

def validate_document(text):

    if not text or not text.strip():

        return {
            "document_type": "Unknown",
            "validation_status": "Needs OCR",
            "validation_reason": "No readable text found"
        }

    # ----------------------------------------------
    # FIRST CHECK STRONG NON-RESUME DOCUMENTS
    # ----------------------------------------------

    invalid_type = detect_invalid_document(text)

    section_count, sections = count_resume_sections(text)

    if invalid_type:

        return {
            "document_type": invalid_type,
            "validation_status": "Invalid",
            "validation_reason": (
                f"Document identified as {invalid_type}, "
                "not a resume"
            )
        }

    # ----------------------------------------------
    # RESUME STRUCTURE CHECK
    # ----------------------------------------------

    if section_count >= 2:

        return {
            "document_type": "Resume",
            "validation_status": "Valid",
            "validation_reason": (
                f"Resume structure detected: "
                f"{', '.join(sections)}"
            )
        }

    # ----------------------------------------------
    # NOT ENOUGH EVIDENCE
    # ----------------------------------------------

    return {
        "document_type": "Unknown",
        "validation_status": "Review Required",
        "validation_reason": (
            "Document does not contain enough "
            "resume-specific sections"
        )
    }


# --------------------------------------------------
# PROCESS ONE DOCUMENT
# --------------------------------------------------

def process_document(resume):

    resume_id = resume["id"]
    filename = resume["filename"]
    extracted_text = resume["extracted_text"]

    print("----------------------------------------")
    print(f"Resume ID: {resume_id}")
    print(f"File: {filename}")

    result = validate_document(extracted_text)

    conn = get_connection()

    try:

        # ------------------------------------------
        # VALID RESUME
        # ------------------------------------------

        if result["validation_status"] == "Valid":

            conn.execute(
                """
                UPDATE resumes
                SET
                    document_type = ?,
                    validation_status = ?,
                    validation_reason = ?,
                    status = ?,
                    processing_stage = ?
                WHERE id = ?
                """,
                (
                    result["document_type"],
                    result["validation_status"],
                    result["validation_reason"],
                    "Extracted",
                    "Extracted",
                    resume_id
                )
            )

            print("Document Type: Resume")
            print("Validation: VALID")
            print("Processing Stage: Extracted")

        # ------------------------------------------
        # INVALID DOCUMENT
        # ------------------------------------------

        elif result["validation_status"] == "Invalid":

            conn.execute(
                """
                UPDATE resumes
                SET
                    document_type = ?,
                    validation_status = ?,
                    validation_reason = ?,
                    status = ?,
                    processing_stage = ?
                WHERE id = ?
                """,
                (
                    result["document_type"],
                    result["validation_status"],
                    result["validation_reason"],
                    "Invalid Resume",
                    "Rejected",
                    resume_id
                )
            )

            print(f"Document Type: {result['document_type']}")
            print("Validation: INVALID")
            print("Processing Stage: Rejected")

        # ------------------------------------------
        # OCR REQUIRED
        # ------------------------------------------

        elif result["validation_status"] == "Needs OCR":

            conn.execute(
                """
                UPDATE resumes
                SET
                    document_type = ?,
                    validation_status = ?,
                    validation_reason = ?,
                    status = ?,
                    processing_stage = ?
                WHERE id = ?
                """,
                (
                    result["document_type"],
                    result["validation_status"],
                    result["validation_reason"],
                    "Needs OCR",
                    "OCR Required",
                    resume_id
                )
            )

            print("Document Type: Unknown")
            print("Validation: OCR REQUIRED")

        # ------------------------------------------
        # REVIEW REQUIRED
        # ------------------------------------------

        else:

            conn.execute(
                """
                UPDATE resumes
                SET
                    document_type = ?,
                    validation_status = ?,
                    validation_reason = ?
                WHERE id = ?
                """,
                (
                    result["document_type"],
                    result["validation_status"],
                    result["validation_reason"],
                    resume_id
                )
            )

            print("Document Type: Unknown")
            print("Validation: REVIEW REQUIRED")

        conn.commit()

    except Exception as e:

        print(f"ERROR: {e}")

    finally:

        conn.close()


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    conn = get_connection()

    # Process every document that has readable extracted text.
    # This allows previously rejected documents to be
    # validated again after improving the validation logic.

    resumes = conn.execute(
        """
        SELECT
            id,
            filename,
            extracted_text
        FROM resumes
        WHERE extracted_text IS NOT NULL
          AND extracted_text != ''
        ORDER BY id
        """
    ).fetchall()

    conn.close()

    if not resumes:

        print("No extracted documents found.")
        return

    print(f"Found {len(resumes)} extracted document(s).")

    for resume in resumes:

        process_document(resume)

    print("----------------------------------------")
    print("Document validation finished.")


# --------------------------------------------------
# START
# --------------------------------------------------

if __name__ == "__main__":
    main()