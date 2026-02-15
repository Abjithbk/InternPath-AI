from langchain_core.tools import tool
from duckduckgo_search import DDGS

@tool(description="Search latest info from internet")
def web_search(query: str) -> str:
    """Search latest info from internet."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            return "\n".join([r["body"] for r in results])
    except Exception as e:
        return f"Search failed: {str(e)}"



def should_use_web_search(user_input: str) -> bool:
    """
    Determine if query needs real-time web search
    Returns True if user is asking about current/dynamic information
    """
    user_input = user_input.lower()
    
    # Category 1: TIME-SENSITIVE (always search)
    time_keywords = [
        "current", "latest", "recent", "now", "today", 
        "2024", "2025", "2026", "this year", "upcoming", "new"
    ]
    
    # Category 2: JOB MARKET (high priority)
    job_market_keywords = [
        "hiring", "recruitment", "openings", "vacancies", 
        "job opportunities", "positions", "recruiting",
        "job market", "placement", "campus placement"
    ]
    
    # Category 3: INTERNSHIPS
    internship_keywords = [
        "internship", "intern", "summer internship", 
        "winter internship", "stipend", "training"
    ]
    
    # Category 4: SALARY & COMPENSATION
    salary_keywords = [
        "salary", "package", "ctc", "lpa", "stipend",
        "pay", "compensation", "per annum", "wage"
    ]
    
    # Category 5: TRENDING TECH & SKILLS
    trending_keywords = [
        "trending", "in-demand", "hot skills", "popular",
        "emerging", "top skills", "demand", "required skills"
    ]
    
    # Category 6: COMPANIES
    company_keywords = [
        "companies hiring", "top companies", "best companies",
        "startups", "mnc", "faang", "maang", "product based"
    ]
    
    # Category 7: STATISTICS & COMPARISONS
    data_keywords = [
        "statistics", "data", "report", "survey",
        "vs", "compare", "comparison", "worth it"
    ]
    
    # Category 8: SPECIFIC PLATFORMS
    platform_keywords = [
        "linkedin", "naukri", "indeed", "glassdoor",
        "internshala", "unstop", "geeksforgeeks"
    ]
    
    # Combine all categories
    all_keywords = (
        time_keywords + job_market_keywords + internship_keywords +
        salary_keywords + trending_keywords + company_keywords +
        data_keywords + platform_keywords
    )
    
    # Check if any keyword matches
    return any(keyword in user_input for keyword in all_keywords)        