import sqlite3
import os


DB_NAME = os.path.join(
    os.path.dirname(__file__),
    "jobs.db"
)


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def add_column_if_missing(conn, table, column, definition):

    columns = [
        row["name"]
        for row in conn.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()
    ]

    if column not in columns:
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        )


def init_db():

    conn = get_connection()

    # -------------------------
    # JOBS TABLE
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            job_name TEXT NOT NULL,
            skills TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Optional Job Description
    add_column_if_missing(
        conn,
        "jobs",
        "job_description",
        "TEXT"
    )

    # -------------------------
    # RESUMES TABLE
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            status TEXT DEFAULT 'Queued',
            score REAL,
            extracted_text TEXT
        )
    """)

    # -------------------------
    # CANDIDATE DETAILS
    # -------------------------

    add_column_if_missing(
        conn, "resumes", "name", "TEXT"
    )

    add_column_if_missing(
        conn, "resumes", "email", "TEXT"
    )

    add_column_if_missing(
        conn, "resumes", "phone", "TEXT"
    )

    add_column_if_missing(
        conn, "resumes", "skills", "TEXT"
    )

    add_column_if_missing(
        conn, "resumes", "experience", "TEXT"
    )

    add_column_if_missing(
        conn, "resumes", "education", "TEXT"
    )

    add_column_if_missing(
        conn, "resumes", "projects", "TEXT"
    )

    # -------------------------
    # DOCUMENT VALIDATION
    # -------------------------

    add_column_if_missing(
        conn, "resumes", "document_type", "TEXT"
    )

    add_column_if_missing(
        conn, "resumes", "validation_status", "TEXT"
    )

    add_column_if_missing(
        conn, "resumes", "validation_reason", "TEXT"
    )

    # -------------------------
    # SKILL MATCHING
    # -------------------------

    add_column_if_missing(
        conn, "resumes", "matched_skills", "TEXT"
    )

    add_column_if_missing(
        conn, "resumes", "missing_skills", "TEXT"
    )

    # -------------------------
    # PROCESSING PIPELINE
    # -------------------------

    add_column_if_missing(
        conn,
        "resumes",
        "processing_stage",
        "TEXT DEFAULT 'Queued'"
    )

    # -------------------------
    # AI SCORING DETAILS
    # -------------------------

    add_column_if_missing(
        conn,
        "resumes",
        "skill_coverage",
        "REAL"
    )

    add_column_if_missing(
        conn,
        "resumes",
        "semantic_relevance",
        "REAL"
    )

    add_column_if_missing(
        conn,
        "resumes",
        "jd_relevance",
        "REAL"
    )

    add_column_if_missing(
        conn,
        "resumes",
        "ai_recommendation",
        "TEXT DEFAULT 'Review'"
    )


    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")