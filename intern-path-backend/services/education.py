from decimal import Decimal


def score_education(profile: dict):
    score = 0
    feedback = []

    college = profile.get("college")
    course = profile.get("course") or profile.get("department")
    cgpa = profile.get("cgpa")
    year = profile.get("year")
    semester = profile.get("semester")

    if isinstance(year, int) and 1 <= year <= 4:
        score += 1
    else:
        feedback.append({
            "area": "education",
            "severity": "low",
            "summary": "Academic year missing or invalid.",
            "reasons": ["Year should be between 1 and 4"],
            "action": "Provide your current year (1-4)."
        })

    if isinstance(semester, int) and 1 <= semester <= 8:
        score += 1
    else:
        feedback.append({
            "area": "education",
            "severity": "low",
            "summary": "Semester missing or invalid.",
            "reasons": ["Semester should be between 1 and 8"],
            "action": "Provide your current semester (1-8)."
        })

   
    if college:
        score += 2
    else:
        feedback.append({
            "area": "education",
            "severity": "medium",
            "summary": "College name missing.",
            "reasons": ["College name is not provided"],
            "action": "Add your college or university name."
        })

   
    if course:
        score += 2
    else:
        feedback.append({
            "area": "education",
            "severity": "medium",
            "summary": "Course name missing.",
            "reasons": ["Course or degree name is not provided"],
            "action": "Add your course or degree name."
        })

   
    if isinstance(cgpa, (int, float, Decimal)):
        cgpa_val = float(cgpa)
        if cgpa_val >= 9.0:
            score += 14
        elif cgpa_val >= 8.0:
            score += 10
            feedback.append({
                "area": "education",
                "severity": "low",
                "summary": "CGPA could be higher.",
                "reasons": ["CGPA is below 9.0"],
                "action": "Improve CGPA to 9.0+ to maximize education score."
            })
        else:
            score += 6
            feedback.append({
                "area": "education",
                "severity": "medium",
                "summary": "Low CGPA.",
                "reasons": ["CGPA is significantly below expected threshold"],
                "action": "Focus on improving academic performance."
            })
    else:
        feedback.append({
            "area": "education",
            "severity": "high",
            "summary": "CGPA missing.",
            "reasons": ["CGPA is not provided"],
            "action": "Add your CGPA."
        })

    return {
        "education_score": score,
        "feedback": feedback
    }
