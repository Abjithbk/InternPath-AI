

ACTION_VERBS = [
    "implemented", "built", "designed", "developed",
    "optimized", "automated", "deployed", "integrated",
    "reduced", "improved", "engineered", "created"
]

ADVANCED_STACK = {
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

INTERMEDIATE_STACK = {
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

BEGINNER_STACK = {
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


def score_projects(projects: list):
    result = {
        "project_score": 0,
        "feedback": [],            
        "project_feedback": []    
    }

   
    if not projects:
        result["feedback"].append({
            "area": "projects",
            "severity": "high",
            "summary": "No projects found.",
            "reasons": ["No hands-on development work listed"],
            "action": "Add at least 2–3 real-world projects."
        })
        return result

    section_reasons = []

  
   
    count = len(projects)
    if count == 1:
        quantity_score = 15
        section_reasons.append("Only one project listed")
    elif count == 2:
        quantity_score = 20
    else:
        quantity_score = 25

    long_desc_count = 0
    action_count = 0
    stack_penalty = 0   

    
    for project in projects:
        title = project.get("title", "Untitled Project")
        desc = project.get("description", "").strip().lower()
        tech_stack = project.get("tech_stack", [])

        issues = []

        
        if len(desc) > 150:
            long_desc_count += 1
        else:
            issues.append("Project description is too short or vague")

        
        if any(v in desc for v in ACTION_VERBS):
            action_count += 1
        else:
            issues.append("No action verbs showing implementation or impact")

       
        if tech_stack:
            stack_lower = {s.lower() for s in tech_stack}
            if stack_lower & ADVANCED_STACK:
                stack_level = "strong"
            elif stack_lower & INTERMEDIATE_STACK:
                stack_level = "moderate"
            elif stack_lower & BEGINNER_STACK:
                stack_level = "weak"
            else:
                stack_level = "unknown"
        else:
            stack_level = "missing"

      
        if stack_level == "weak":
            stack_penalty += 3
            issues.append(
                "Project uses only basic technologies; lacks backend, framework, or deployment tools"
            )
        elif stack_level == "missing":
            stack_penalty += 5
            issues.append("No tech stack specified for this project")

       
        stack_penalty = min(stack_penalty, 10)

        
        if issues:
            result["project_feedback"].append({
                "project": title,
                "severity": "needs_improvement",
                "issues": issues,
                "action": (
                    "Strengthen this project by improving the tech stack, "
                    "adding backend/database components, and clearly explaining implementation."
                )
            })
        else:
            result["project_feedback"].append({
                "project": title,
                "severity": "strong",
                "summary": "This project demonstrates strong technical execution and stack choice.",
                "highlights": [
                    "Appropriate technology stack",
                    "Clear implementation details",
                    "Good real-world relevance"
                ],
                "action": "This project is strong enough for internships and interviews."
            })

  
    if long_desc_count == 0:
        description_score = 0
        section_reasons.append("All project descriptions are weak or too short")
    elif long_desc_count == 1:
        description_score = 5
        section_reasons.append("Only one project has a detailed description")
    elif long_desc_count == 2:
        description_score = 10
    else:
        description_score = 15

 
    if action_count == 0:
        action_score = 0
        section_reasons.append("No projects demonstrate clear implementation")
    elif action_count == 1:
        action_score = 5
        section_reasons.append("Limited use of action-oriented language")
    elif action_count == 2:
        action_score = 10
    else:
        action_score = 15

  
    final_score = quantity_score + description_score + action_score
    final_score -= stack_penalty
    final_score = max(0, min(final_score, 55))

    result["project_score"] = final_score

    
    if section_reasons:
        result["feedback"].append({
            "area": "projects",
            "severity": "medium" if final_score >= 40 else "high",
            "summary": "Project section needs improvement.",
            "reasons": section_reasons,
            "action": "Improve project depth, execution clarity, and technology choices."
        })

    return result
