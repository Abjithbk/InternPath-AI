def aggregate_feedback(education, skills, projects):
    feedback = []
    feedback.extend(projects.get("feedback", []))
    feedback.extend(skills.get("feedback", []))
    feedback.extend(education.get("feedback", []))
    return feedback[:5]
