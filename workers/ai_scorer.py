import re

from sentence_transformers import SentenceTransformer, util


# --------------------------------------------------
# LOAD AI MODEL
# --------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------------------------
# NORMALIZE TEXT
# --------------------------------------------------

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
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# --------------------------------------------------
# GET REQUIRED SKILLS
# --------------------------------------------------

def get_required_skills(job_skills):

    if not job_skills:
        return []

    job_skills = normalize(job_skills)

    skills = re.split(r"[,;|.]", job_skills)

    result = []

    for skill in skills:

        skill = normalize(skill.strip())

        if skill and skill not in result:
            result.append(skill)

    return result

# --------------------------------------------------
# CHECK WHETHER A SKILL EXISTS
# --------------------------------------------------

def skill_exists(skill, resume_text):

    skill = normalize(skill)
    resume_text = normalize(resume_text)

    if not skill or not resume_text:
        return False

    pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

    return bool(re.search(pattern, resume_text))


# --------------------------------------------------
# CALCULATE SKILL MATCH
# --------------------------------------------------

def calculate_skill_match(required_skills, resume_text):

    matched_skills = []
    missing_skills = []

    for skill in required_skills:

        if skill_exists(skill, resume_text):
            matched_skills.append(skill)

        else:
            missing_skills.append(skill)

    if required_skills:

        skill_coverage = (
            len(matched_skills) /
            len(required_skills)
        ) * 100

    else:

        skill_coverage = 0

    return (
        round(skill_coverage),
        matched_skills,
        missing_skills
    )


# --------------------------------------------------
# CALCULATE SEMANTIC RELEVANCE
# --------------------------------------------------

def calculate_semantic_score(job_skills, resume_text):

    job_text = normalize(job_skills)
    resume_text = normalize(resume_text)

    if not job_text or not resume_text:
        return 0

    job_embedding = model.encode(
        job_text,
        convert_to_tensor=True
    )

    resume_embedding = model.encode(
        resume_text,
        convert_to_tensor=True
    )

    similarity = util.cos_sim(
        job_embedding,
        resume_embedding
    ).item()

    # Keep similarity between 0 and 1

    similarity = max(
        0,
        min(1, similarity)
    )

    return round(similarity * 100)


# --------------------------------------------------
# CALCULATE FINAL SCORE
# --------------------------------------------------

def calculate_score(job_skills, resume_text):

    if not resume_text:

        return {
            "score": 0,
            "skill_coverage": 0,
            "semantic_relevance": 0,
            "matched_skills": [],
            "missing_skills": []
        }

    resume_text = normalize(resume_text)

    required_skills = get_required_skills(
        job_skills
    )

    # --------------------------------------------------
    # SKILL MATCH
    # --------------------------------------------------

    skill_coverage, matched_skills, missing_skills = (
        calculate_skill_match(
            required_skills,
            resume_text
        )
    )

    # --------------------------------------------------
    # SEMANTIC MATCH
    # --------------------------------------------------

    semantic_relevance = calculate_semantic_score(
        job_skills,
        resume_text
    )

    # --------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------

    skill_points = skill_coverage * 0.50

    semantic_points = semantic_relevance * 0.50

    final_score = round(
        skill_points + semantic_points
    )

    final_score = max(
        0,
        min(100, final_score)
    )

    return {
    "score": final_score,
    "skill_coverage": skill_coverage,
    "semantic_relevance": semantic_relevance,
    "matched_skills": matched_skills,
    "missing_skills": missing_skills
}