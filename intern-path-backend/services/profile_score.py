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


def score_user_profile(profile: dict):
    edu = score_education(profile)
    skills = score_skills(profile.get("skills", []))
    projects = score_projects(profile.get("projects", []))

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