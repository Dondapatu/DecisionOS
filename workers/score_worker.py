import os
import sys


# -----------------------------------
# FIND BACKEND FOLDER
# -----------------------------------

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

BACKEND = os.path.join(
    ROOT,
    "backend"
)

sys.path.insert(0, BACKEND)


# -----------------------------------
# IMPORT DATABASE + AI SCORER
# -----------------------------------

from database import get_connection
from ai_scorer import calculate_score


# -----------------------------------
# PROCESS ONE RESUME
# -----------------------------------

def process_resume(resume):

    resume_id = resume["id"]
    job_id = resume["job_id"]
    filename = resume["filename"]
    extracted_text = resume["extracted_text"]

    print("----------------------------------------")
    print(f"Resume ID: {resume_id}")
    print(f"File: {filename}")

    conn = get_connection()

    try:

        # -----------------------------------
        # GET JOB DETAILS
        # -----------------------------------

        job = conn.execute(
            """
            SELECT
                job_name,
                skills
            FROM jobs
            WHERE id = ?
            """,
            (job_id,)
        ).fetchone()

        if not job:

            print("ERROR: Job not found")

            return

        job_name = job["job_name"]
        job_skills = job["skills"]

        print(f"Job: {job_name}")
        print(f"Required Skills: {job_skills}")


        # -----------------------------------
        # MARK AS SCORING
        # -----------------------------------

        conn.execute(
            """
            UPDATE resumes
            SET
                status = ?,
                processing_stage = ?
            WHERE id = ?
            """,
            (
                "Scoring",
                "Scoring",
                resume_id
            )
        )

        conn.commit()


        # -----------------------------------
        # CALCULATE AI SCORE
        # -----------------------------------

        result = calculate_score(
            job_skills,
            extracted_text
        )


        # -----------------------------------
        # GET RESULTS
        # -----------------------------------

        score = result["score"]

        skill_coverage = result["skill_coverage"]

        semantic_relevance = result["semantic_relevance"]

        matched_skills = result["matched_skills"]

        missing_skills = result["missing_skills"]


        # -----------------------------------
        # AI RECOMMENDATION
        # -----------------------------------

        if score > 60:

            ai_recommendation = "Shortlist"

        else:

            ai_recommendation = "Review"


        # -----------------------------------
        # SAVE RESULTS
        # -----------------------------------

        conn.execute(
            """
            UPDATE resumes
            SET
                score = ?,
                skill_coverage = ?,
                semantic_relevance = ?,
                matched_skills = ?,
                missing_skills = ?,
                ai_recommendation = ?,
                status = ?,
                processing_stage = ?
            WHERE id = ?
            """,
            (
                score,
                skill_coverage,
                semantic_relevance,
                ", ".join(matched_skills),
                ", ".join(missing_skills),
                ai_recommendation,
                "Scored",
                "Scored",
                resume_id
            )
        )

        conn.commit()


        # -----------------------------------
        # SHOW RESULTS
        # -----------------------------------

        print(f"AI Score: {score}")

        print(
            f"Skill Coverage: "
            f"{skill_coverage}%"
        )

        print(
            f"Semantic Relevance: "
            f"{semantic_relevance}%"
        )

        print(
            f"Matched Skills: "
            f"{matched_skills}"
        )

        print(
            f"Missing Skills: "
            f"{missing_skills}"
        )

        print(
            f"AI Recommendation: "
            f"{ai_recommendation}"
        )

        print("Scoring successful")


    except Exception as e:

        print(f"ERROR: {e}")

        # -----------------------------------
        # MARK AS FAILED
        # -----------------------------------

        conn.execute(
            """
            UPDATE resumes
            SET
                status = ?,
                processing_stage = ?
            WHERE id = ?
            """,
            (
                "Failed",
                "Failed",
                resume_id
            )
        )

        conn.commit()


    finally:

        conn.close()


# -----------------------------------
# MAIN WORKER
# -----------------------------------

def main():

    conn = get_connection()

    resumes = conn.execute(
        """
        SELECT
            id,
            job_id,
            filename,
            extracted_text
        FROM resumes
        WHERE processing_stage = 'Extracted'
          AND extracted_text IS NOT NULL
          AND extracted_text != ''
        ORDER BY id
        """
    ).fetchall()

    conn.close()


    # -----------------------------------
    # NO RESUMES
    # -----------------------------------

    if not resumes:

        print(
            "No resumes ready for scoring."
        )

        return


    print(
        f"Found {len(resumes)} "
        f"resume(s) ready for scoring."
    )


    # -----------------------------------
    # PROCESS RESUMES
    # -----------------------------------

    for resume in resumes:

        process_resume(resume)


    print("----------------------------------------")

    print("Scoring worker finished.")


# -----------------------------------
# START WORKER
# -----------------------------------

if __name__ == "__main__":

    main()