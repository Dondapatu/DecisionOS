import os
import sys

# Project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import backend/database.py
BACKEND = os.path.join(ROOT, "backend")
sys.path.insert(0, BACKEND)

from database import get_connection


def sync_uploads():
    conn = get_connection()

    upload_root = os.path.join(BACKEND, "uploads")

    if not os.path.exists(upload_root):
        print("Uploads folder not found.")
        return

    for job_id in os.listdir(upload_root):
        job_folder = os.path.join(upload_root, job_id)

        if not os.path.isdir(job_folder):
            continue

        # Skip folders that don't belong to an existing job
        job = conn.execute(
            "SELECT id FROM jobs WHERE id=?",
            (job_id,)
        ).fetchone()

        if not job:
            print(f"Skipping missing job: {job_id}")
            continue

        for filename in os.listdir(job_folder):
            file_path = os.path.join(job_folder, filename)

            if not os.path.isfile(file_path):
                continue

            exists = conn.execute(
                "SELECT id FROM resumes WHERE job_id=? AND filename=?",
                (job_id, filename)
            ).fetchone()

            if not exists:
                conn.execute(
                    """
                    INSERT INTO resumes
                    (job_id, filename, status)
                    VALUES (?, ?, ?)
                    """,
                    (job_id, filename, "Queued")
                )

                print(f"Recovered: {filename}")

    conn.commit()
    conn.close()

    print("Recovery Complete.")


if __name__ == "__main__":
    sync_uploads()