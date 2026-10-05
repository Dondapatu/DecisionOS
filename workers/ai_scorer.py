import re

from sentence_transformers import SentenceTransformer, util


model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------------------------------------
# TEXT NORMALIZATION
# ---------------------------------------------------------

def normalize(text):

    if not text:
        return ""

    text = text.lower()

    replacements = {
        "llms": "llm",
        "react.js": "react",
        "reactjs": "react",
        "node.js": "node",
        "nodejs": "node",
        "rest apis": "rest api",
        "restful apis": "rest api",
        "fast api": "fastapi",
        "postgres": "postgresql",
        "postgresql database": "postgresql",
        "machine learning": "machine learning",
        "artificial intelligence": "artificial intelligence",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"([a-z])([A-Z])",
        r"\1 \2",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ---------------------------------------------------------
# REQUIRED SKILLS
# ---------------------------------------------------------

def get_required_skills(job_skills):

    if not job_skills:
        return []

    job_skills = normalize(job_skills)

    skills = re.split(
        r"[,;|.]",
        job_skills
    )

    result = []

    for skill in skills:

        skill = normalize(
            skill.strip()
        )

        if skill and skill not in result:
            result.append(skill)

    return result


# ---------------------------------------------------------
# EXACT SKILL CHECK
# ---------------------------------------------------------

def skill_exists(skill, resume_text):

    skill = normalize(skill)
    resume_text = normalize(resume_text)

    if not skill or not resume_text:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(skill)
        + r"(?!\w)"
    )

    return bool(
        re.search(
            pattern,
            resume_text
        )
    )


# ---------------------------------------------------------
# EQUIVALENT SKILLS
#
# These are treated as full evidence.
# Example:
# SQL requirement + MySQL in resume
# ---------------------------------------------------------

EQUIVALENT_SKILLS = {

    "sql": [
        "mysql",
        "postgresql",
        "sqlite",
        "mariadb",
    ],

}


# ---------------------------------------------------------
# RELATED SKILLS
#
# These are not exact replacements.
# They receive partial evidence.
#
# Example:
# FastAPI requirement + Flask experience
# = related backend experience
# ---------------------------------------------------------

RELATED_SKILLS = {

    "fastapi": [
        "flask",
        "django",
        "rest api",
    ],

    "flask": [
        "fastapi",
        "django",
        "rest api",
    ],

    "django": [
        "fastapi",
        "flask",
        "rest api",
    ],

    "rest api": [
        "fastapi",
        "flask",
        "django",
    ],

}


# ---------------------------------------------------------
# SKILL MATCHING
# ---------------------------------------------------------

def calculate_skill_match(
    required_skills,
    resume_text
):

    matched_skills = []
    missing_skills = []

    total_evidence = 0

    for required_skill in required_skills:

        # ---------------------------------------------
        # 1. EXACT MATCH
        # ---------------------------------------------

        if skill_exists(
            required_skill,
            resume_text
        ):

            matched_skills.append(
                required_skill
            )

            total_evidence += 1

            continue

        # ---------------------------------------------
        # 2. EQUIVALENT MATCH
        # ---------------------------------------------

        equivalent_found = False

        for equivalent in EQUIVALENT_SKILLS.get(
            required_skill,
            []
        ):

            if skill_exists(
                equivalent,
                resume_text
            ):

                matched_skills.append(
                    f"{required_skill} "
                    f"(equivalent: {equivalent})"
                )

                total_evidence += 1

                equivalent_found = True

                break

        if equivalent_found:
            continue

        # ---------------------------------------------
        # 3. RELATED MATCH
        # ---------------------------------------------

        related_found = False

        for related in RELATED_SKILLS.get(
            required_skill,
            []
        ):

            if skill_exists(
                related,
                resume_text
            ):

                matched_skills.append(
                    f"{required_skill} "
                    f"(related: {related})"
                )

                total_evidence += 0.5

                related_found = True

                break

        if related_found:
            continue

        # ---------------------------------------------
        # 4. NO EVIDENCE
        # ---------------------------------------------

        missing_skills.append(
            required_skill
        )

    # ---------------------------------------------
    # FINAL SKILL COVERAGE
    # ---------------------------------------------

    if required_skills:

        skill_coverage = (
            total_evidence
            / len(required_skills)
        ) * 100

    else:

        skill_coverage = 0

    return (
        round(skill_coverage),
        matched_skills,
        missing_skills
    )


# ---------------------------------------------------------
# RESUME SECTION EXTRACTION
# ---------------------------------------------------------

def get_resume_sections(resume_text):

    text = normalize(resume_text)

    sections = {

        "summary": "",

        "experience": "",

        "skills": "",

        "projects": "",

        "education": ""

    }

    patterns = {

        "summary":
            r"(summary|professional summary|profile)"
            r"(.*?)"
            r"(?=experience|work experience|employment|"
            r"education|technical skills|skills|projects|$)",

        "experience":
            r"(experience|work experience|employment history)"
            r"(.*?)"
            r"(?=education|technical skills|skills|projects|"
            r"certifications|$)",

        "skills":
            r"(technical skills|skills|technical expertise)"
            r"(.*?)"
            r"(?=experience|education|projects|certifications|$)",

        "projects":
            r"(projects|academic projects|personal projects)"
            r"(.*?)"
            r"(?=experience|education|technical skills|"
            r"skills|certifications|$)",

        "education":
            r"(education|education and training)"
            r"(.*?)"
            r"(?=technical skills|skills|projects|experience|"
            r"certifications|$)"
    }

    for section_name, pattern in patterns.items():

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            sections[section_name] = match.group(0)

    return sections


# ---------------------------------------------------------
# GENERAL SEMANTIC SIMILARITY
# ---------------------------------------------------------

def semantic_similarity(
    source_text,
    target_text
):

    source_text = normalize(
        source_text
    )

    target_text = normalize(
        target_text
    )

    if not source_text or not target_text:
        return 0

    source_embedding = model.encode(
        source_text,
        convert_to_tensor=True
    )

    target_embedding = model.encode(
        target_text,
        convert_to_tensor=True
    )

    similarity = util.cos_sim(
        source_embedding,
        target_embedding
    )

    score = float(
        similarity[0][0]
    )

    score = max(
        0,
        min(1, score)
    )

    return round(
        score * 100
    )


# ---------------------------------------------------------
# RESUME RELEVANCE
# ---------------------------------------------------------

def calculate_resume_relevance(
    job_skills,
    resume_text
):

    if not job_skills or not resume_text:
        return 0

    sections = get_resume_sections(
        resume_text
    )

    useful_sections = []

    for section_name in [
        "summary",
        "experience",
        "skills",
        "projects"
    ]:

        section_text = sections.get(
            section_name,
            ""
        )

        if section_text:

            useful_sections.append(
                section_text
            )

    if not useful_sections:

        useful_sections = [
            normalize(resume_text)
        ]

    job_embedding = model.encode(
        normalize(job_skills),
        convert_to_tensor=True
    )

    section_embeddings = model.encode(
        useful_sections,
        convert_to_tensor=True
    )

    similarities = util.cos_sim(
        job_embedding,
        section_embeddings
    )[0]

    best_similarity = float(
        similarities.max()
    )

    best_similarity = max(
        0,
        min(1, best_similarity)
    )

    return round(
        best_similarity * 100
    )


# ---------------------------------------------------------
# JOB DESCRIPTION RELEVANCE
# ---------------------------------------------------------

def calculate_jd_relevance(
    job_description,
    resume_text
):

    if not job_description:
        return None

    if not resume_text:
        return 0

    return semantic_similarity(
        job_description,
        resume_text
    )


# ---------------------------------------------------------
# FINAL SCORE
# ---------------------------------------------------------

def calculate_score(
    job_skills,
    resume_text,
    job_description=None
):

    if not resume_text:

        return {

            "score": 0,

            "skill_coverage": 0,

            "semantic_relevance": 0,

            "jd_relevance": None,

            "matched_skills": [],

            "missing_skills": []

        }

    resume_text = normalize(
        resume_text
    )

    required_skills = get_required_skills(
        job_skills
    )

    (
        skill_coverage,
        matched_skills,
        missing_skills
    ) = calculate_skill_match(
        required_skills,
        resume_text
    )

    semantic_relevance = calculate_resume_relevance(
        job_skills,
        resume_text
    )

    jd_relevance = calculate_jd_relevance(
        job_description,
        resume_text
    )

    # ---------------------------------------------
    # JOB WITH JD
    # ---------------------------------------------

    if jd_relevance is not None:

        final_score = (

            skill_coverage * 0.40

            + semantic_relevance * 0.30

            + jd_relevance * 0.30

        )

    # ---------------------------------------------
    # JOB WITHOUT JD
    # ---------------------------------------------

    else:

        final_score = (

            skill_coverage * 0.50

            + semantic_relevance * 0.50

        )

    final_score = round(
        final_score
    )

    final_score = max(
        0,
        min(100, final_score)
    )

    return {

        "score": final_score,

        "skill_coverage": skill_coverage,

        "semantic_relevance": semantic_relevance,

        "jd_relevance": jd_relevance,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills

    }