import json

from services.education import score_education
from services.skills import score_skills
from services.projects import score_projects
from services.feedback import aggregate_feedback


def readiness_level(score: int) -> str:
    if score < 40:
        return "Low"
    elif score < 70:
        return "Medium"
    return "High"


def _normalize_skills(skills_raw):
    if isinstance(skills_raw, list):
        return [str(s) for s in skills_raw if s]
    if isinstance(skills_raw, str):
        try:
            parsed = json.loads(skills_raw)
            if isinstance(parsed, list):
                return [str(s) for s in parsed if s]
        except (json.JSONDecodeError, TypeError):
            pass
    return []


def _normalize_projects(projects_raw):
    if isinstance(projects_raw, list):
        return [p for p in projects_raw if isinstance(p, dict)]
    if isinstance(projects_raw, str):
        try:
            parsed = json.loads(projects_raw)
            if isinstance(parsed, list):
                return [p for p in parsed if isinstance(p, dict)]
        except (json.JSONDecodeError, TypeError):
            pass
    return []


def score_user_profile(profile: dict):
    normalized_profile = dict(profile)
    normalized_profile["skills"] = _normalize_skills(profile.get("skills", []))
    normalized_profile["projects"] = _normalize_projects(profile.get("projects", []))

    edu = score_education(normalized_profile)
    skills = score_skills(normalized_profile.get("skills", []))
    projects = score_projects(normalized_profile.get("projects", []))

    education_score = edu["education_score"]
    skills_score = skills["skills_score"]
    project_score = projects["project_score"]

    final_score = min(education_score + skills_score + project_score, 100)

    feedback = aggregate_feedback(edu, skills, projects)

    if not feedback:
        feedback = [{
            "area": "overall",
            "severity": "success",
            "summary": "You are internship-ready.",
            "reasons": [
                "Strong academic performance",
                "Relevant technical skills",
                "High-quality real-world projects"
            ],
            "action": "Start applying confidently to internships."
        }]

    return {
        "education_score": education_score,
        "skills_score": skills_score,
        "project_score": project_score,
        "final_score": final_score,
        "percentage_score": float(final_score),
        "readiness_level": readiness_level(final_score),
        "feedback": feedback,
        "project_feedback": projects.get("project_feedback", [])
    }