import os
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import uuid
import os
import shutil
from pathlib import Path
from typing import Annotated

from database import get_connection, init_db


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_ROOT = os.path.join(BASE_DIR, "uploads")


# ==================================================
# APP
# ==================================================

app = FastAPI(title="DecisionOS")

init_db()


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv(
            "FRONTEND_URL",
            "http://localhost:5173"
        )
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# JOB MODELS
# ==================================================

class ReviewJob(BaseModel):
    job_name: str
    skills: str
    job_description: str | None = None


class UpdateJob(BaseModel):
    job_name: str | None = None
    skills: str | None = None
    job_description: str | None = None


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():
    return {
        "message": "DecisionOS Backend Running"
    }


# ==================================================
# CREATE JOB
# ==================================================

@app.post("/jobs")
def create_job(job: ReviewJob):

    job_id = str(uuid.uuid4())[:8]

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO jobs
        (
            id,
            job_name,
            skills,
            status,
            job_description
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            job_id,
            job.job_name,
            job.skills,
            "Created",
            job.job_description
        )
    )

    conn.commit()
    conn.close()

    return {
        "id": job_id,
        "job_name": job.job_name,
        "skills": job.skills,
        "job_description": job.job_description,
        "status": "Created"
    }


# ==================================================
# GET ALL JOBS
# ==================================================

@app.get("/jobs")
def get_jobs():

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM jobs
        ORDER BY rowid DESC
        """
    ).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


# ==================================================
# GET ONE JOB
# ==================================================

@app.get("/jobs/{job_id}")
def get_job(job_id: str):

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        """,
        (job_id,)
    ).fetchone()

    conn.close()

    if row:
        return dict(row)

    return {
        "error": "Job not found"
    }


# ==================================================
# UPDATE JOB
# ==================================================

@app.patch("/jobs/{job_id}")
def update_job(
    job_id: str,
    job: UpdateJob
):

    conn = get_connection()

    existing_job = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        """,
        (job_id,)
    ).fetchone()

    if not existing_job:
        conn.close()

        return {
            "error": "Job not found"
        }

    current_job = dict(existing_job)

    job_name = (
        job.job_name
        if job.job_name is not None
        else current_job["job_name"]
    )

    skills = (
        job.skills
        if job.skills is not None
        else current_job["skills"]
    )

    job_description = (
        job.job_description
        if job.job_description is not None
        else current_job.get("job_description")
    )

    conn.execute(
        """
        UPDATE jobs
        SET
            job_name = ?,
            skills = ?,
            job_description = ?
        WHERE id = ?
        """,
        (
            job_name,
            skills,
            job_description,
            job_id
        )
    )

    conn.commit()

    updated_job = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        """,
        (job_id,)
    ).fetchone()

    conn.close()

    return dict(updated_job)


# ==================================================
# UPLOAD RESUMES
# ==================================================

from threading import Lock

pipeline_lock = Lock()


def run_processing_pipeline(job_id: str):

    if not pipeline_lock.acquire(blocking=False):
        return

    try:

        import sys

        workers_path = os.path.join(
            os.path.dirname(BASE_DIR),
            "workers"
        )

        if workers_path not in sys.path:
            sys.path.insert(0, workers_path)

        import importlib

        extract_worker = importlib.import_module(
            "extract_worker"
        )

        score_worker = importlib.import_module(
            "score_worker"
        )

        extract_resume = extract_worker.process_resume
        score_resume = score_worker.process_resume

        # -----------------------------
        # STEP 1: Extract resumes
        # -----------------------------

        conn = get_connection()

        resumes = conn.execute(
            """
            SELECT *
            FROM resumes
            WHERE job_id = ?
              AND processing_stage = 'Queued'
            ORDER BY id
            """,
            (job_id,)
        ).fetchall()

        conn.close()

        for resume in resumes:
            extract_resume(resume)

        # -----------------------------
        # STEP 2: Score resumes
        # -----------------------------

        conn = get_connection()

        resumes = conn.execute(
            """
            SELECT *
            FROM resumes
            WHERE job_id = ?
              AND processing_stage = 'Extracted'
              AND extracted_text IS NOT NULL
              AND extracted_text != ''
            ORDER BY id
            """,
            (job_id,)
        ).fetchall()

        conn.close()

        for resume in resumes:
            score_resume(resume)

    except Exception as e:

        print(
            "Pipeline error:",
            e
        )

    finally:

        pipeline_lock.release()


@app.post("/jobs/{job_id}/upload")
async def upload_resumes(
    job_id: str,
    files: Annotated[
        list[UploadFile],
        File()
    ],
    background_tasks: BackgroundTasks
):

    upload_dir = os.path.join(
        UPLOAD_ROOT,
        job_id
    )

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    conn = get_connection()

    uploaded = []

    for file in files:

        file_path = os.path.join(
            upload_dir,
            file.filename
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        conn.execute(
            """
            INSERT INTO resumes
            (
                job_id,
                filename,
                status,
                score,
                extracted_text
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                job_id,
                file.filename,
                "Queued",
                None,
                None
            )
        )

        uploaded.append(
            file.filename
        )

    conn.commit()
    conn.close()

    background_tasks.add_task(
        run_processing_pipeline,
        job_id
    )

    return {
        "job_id": job_id,
        "uploaded_files": uploaded,
        "count": len(uploaded)
    }


# ==================================================
# GET RESUMES FOR JOB
# ==================================================

@app.get("/jobs/{job_id}/resumes")
def get_resumes(job_id: str):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM resumes
        WHERE job_id = ?
        ORDER BY
            CASE
                WHEN score IS NULL THEN 1
                ELSE 0
            END,
            score DESC,
            id ASC
        """,
        (job_id,)
    ).fetchall()

    conn.close()

    # ----------------------------------------------
    # ADD RANK
    # ----------------------------------------------

    result = []

    rank = 1

    for row in rows:

        data = dict(row)

        if data["score"] is not None:

            data["rank"] = rank

            rank += 1

        else:

            data["rank"] = None

        result.append(data)

    return result


# ==================================================
# GET ONE RESUME
# ==================================================

@app.get("/resume/{resume_id}")
def get_resume(resume_id: int):

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM resumes
        WHERE id = ?
        """,
        (resume_id,)
    ).fetchone()

    conn.close()

    if row:
        return dict(row)

    return {
        "error": "Resume not found"
    }


# ==================================================
# VIEW ORIGINAL RESUME
# ==================================================

@app.get("/resume/{resume_id}/file")
def view_resume_file(resume_id: int):

    conn = get_connection()

    row = conn.execute(
        """
        SELECT job_id, filename
        FROM resumes
        WHERE id = ?
        """,
        (resume_id,)
    ).fetchone()

    conn.close()

    if not row:
        return {
            "error": "Resume not found"
        }

    job_id = row["job_id"]
    filename = row["filename"]

    safe_filename = Path(filename).name

    file_path = os.path.join(
        UPLOAD_ROOT,
        job_id,
        safe_filename
    )

    if not os.path.isfile(file_path):

        return {
            "error": "Resume file not found"
        }

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'inline; filename="{safe_filename}"'
        }
    )


# ==================================================
# UPDATE RESUME STATUS
# ==================================================

@app.post("/resumes/{resume_id}/status")
def update_resume_status(
    resume_id: int,
    status: str
):

    conn = get_connection()

    conn.execute(
        """
        UPDATE resumes
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            resume_id
        )
    )

    conn.commit()
    conn.close()

    return {
        "resume_id": resume_id,
        "status": status
    }


# ==================================================
# SYNC RESUMES
# ==================================================

@app.post("/jobs/{job_id}/sync")
def sync_resumes(job_id: str):

    upload_dir = os.path.join(
        UPLOAD_ROOT,
        job_id
    )

    if not os.path.exists(upload_dir):

        return {
            "message": "Upload folder not found"
        }

    conn = get_connection()

    existing = conn.execute(
        """
        SELECT filename
        FROM resumes
        WHERE job_id = ?
        """,
        (job_id,)
    ).fetchall()

    existing_files = {
        row["filename"]
        for row in existing
    }

    added = 0

    for filename in os.listdir(
        upload_dir
    ):

        if filename not in existing_files:

            conn.execute(
                """
                INSERT INTO resumes
                (
                    job_id,
                    filename,
                    status,
                    score,
                    extracted_text
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    filename,
                    "Queued",
                    None,
                    None
                )
            )

            added += 1

    conn.commit()
    conn.close()

    return {
        "added": added
    }