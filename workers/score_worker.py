import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "backend"
    )
)

from database import get_connection
from ai_scorer import calculate_score


def process_resume(resume):

    conn = get_connection()

    resume_id = resume["id"]
    job_id = resume["job_id"]
    resume_text = resume["extracted_text"]

    if not resume_text:
        conn.close()
        return

    # Get job requirements
    job = conn.execute(
        """
        SELECT skills, job_description
        FROM jobs
        WHERE id = ?
        """,
        (job_id,)
    ).fetchone()

    if not job:
        conn.close()
        return

    job_skills = job["skills"]
    job_description = job["job_description"]

    # Mark as scoring
    conn.execute(
        """
        UPDATE resumes
        SET
            status='Scoring',
            processing_stage='Scoring'
        WHERE id=?
        """,
        (resume_id,)
    )

    conn.commit()

    try:

        # Calculate AI score
        result = calculate_score(
            job_skills,
            resume_text,
            job_description
        )

        score = result["score"]
        skill_coverage = result["skill_coverage"]
        semantic_relevance = result["semantic_relevance"]
        jd_relevance = result["jd_relevance"]

        matched_skills = ", ".join(
            result["matched_skills"]
        )

        missing_skills = ", ".join(
            result["missing_skills"]
        )

        # Classification
        if score >= 61:
            recommendation = "Shortlist"

        elif score >= 50:
            recommendation = "Review"

        elif (
            skill_coverage >= 80
            and (
                semantic_relevance >= 25
                or jd_relevance >= 25
            )
        ):
            recommendation = "Review"

        else:
            recommendation = "Reject"

        # Save complete scoring information
        conn.execute(
            """
            UPDATE resumes
            SET
                score=?,
                skill_coverage=?,
                semantic_relevance=?,
                jd_relevance=?,
                matched_skills=?,
                missing_skills=?,
                ai_recommendation=?,
                status='Scored',
                processing_stage='Scored'
            WHERE id=?
            """,
            (
                score,
                skill_coverage,
                semantic_relevance,
                jd_relevance,
                matched_skills,
                missing_skills,
                recommendation,
                resume_id
            )
        )

        conn.commit()

        print(
            f"Resume {resume_id} scored: "
            f"{score} ({recommendation})"
        )

    except Exception as error:

        conn.execute(
            """
            UPDATE resumes
            SET
                status='Error',
                processing_stage='Error'
            WHERE id=?
            """,
            (resume_id,)
        )

        conn.commit()

        print(
            f"Error scoring resume {resume_id}: {error}"
        )

    finally:
        conn.close()


def process_resumes():

    conn = get_connection()

    resumes = conn.execute(
        """
        SELECT *
        FROM resumes
        WHERE
            processing_stage='Extracted'
            AND extracted_text IS NOT NULL
            AND extracted_text != ''
        ORDER BY id
        """
    ).fetchall()

    conn.close()

    total_processed = 0

    for resume in resumes:

        process_resume(resume)

        total_processed += 1

    print(
        f"Scoring complete. "
        f"Processed {total_processed} resumes."
    )


if __name__ == "__main__":
    process_resumes()