ADVANCED_SKILLS = {
     "fastapi",
    "spring boot",
    "microservices",
    "docker",
    "docker compose",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "ci/cd",
    "github actions",
    "grpc",
    "graphql",
    "celery",
    "rabbitmq",
    "kafka",
    "terraform",
    "system design",
    "distributed systems",
    "cloud deployment"
}

INTERMEDIATE_SKILLS = {
   "python",
    "django",
    "flask",
    "fastapi basics",
    "java",
    "spring",
    "nodejs",
    "express",
    "react",
    "nextjs",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "rest api",
    "jwt",
    "sqlalchemy",
    "orm",
    "linux",
    "nginx"
}

BEGINNER_SKILLS = {
    "html",
    "css",
    "javascript",
    "bootstrap",
    "tailwind css",
    "jquery",
    "php",
    "sqlite",
    "basic sql",
    "c",
    "cpp",
    "java basics",
    "python basics",
    "git",
    "github",
    "bash",
    "markdown",
    "excel",
    "vs code",
    "json"
}


def score_skills(skills: list):
    score = 0
    feedback = []

    if not skills:
        return {
            "skills_score": 0,
            "feedback": [{
                "area": "skills",
                "severity": "high",
                "summary": "No skills listed.",
                "reasons": ["No technical skills provided"],
                "action": "Add at least 3 technical skills."
            }]
        }

    skills_lower = [s.lower() for s in skills]
    advanced_found = False

    for skill in skills_lower:
        if skill in ADVANCED_SKILLS:
            score += 15
            advanced_found = True
        elif skill in INTERMEDIATE_SKILLS:
            score += 10
        elif skill in BEGINNER_SKILLS:
            score += 5

    if not advanced_found:
        feedback.append({
            "area": "skills",
            "severity": "medium",
            "summary": "No advanced-level skills detected.",
            "reasons": ["Only beginner or intermediate skills listed"],
            "action": "Add at least one advanced to increase the readiness score."
        })

    return {
        "skills_score": min(score, 25),
        "feedback": feedback
    }
