from langchain_core.tools import tool
from ddgs import DDGS  # ✅ Updated import

@tool
def web_search(query: str) -> str:
    """Search latest info from internet."""
    try:
        print(f"🔍 Searching web: '{query}'")
        
        # ✅ New ddgs usage (no context manager needed)
        ddgs = DDGS()
        results = ddgs.text(
            query,
            max_results=5
        )
        
        # Convert to list
        results = list(results)
        
        if not results:
            print("⚠️ No results from DDGS")
            return "No current information found from web search."
        
        print(f"✅ Found {len(results)} results")
        
        output = []
        for i, r in enumerate(results[:3], 1):  # Use top 3 results
            title = r.get('title', 'No title')
            body = r.get('body', '')
            link = r.get('href', '')
            
            # Format each result clearly
            result_text = f"""
{i}. {title}
{body}
Link: {link}
"""
            output.append(result_text)
        
        full_output = "\n".join(output)
        print(f"📄 Output length: {len(full_output)} chars")
        print(f"📄 Preview: {full_output[:200]}...")
        
        return full_output
        
    except Exception as e:
        import traceback
        print(f"❌ Web search error: {e}")
        traceback.print_exc()
        return f"Web search unavailable: {str(e)}"


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
        "startups", "mnc", "faang", "maang", "product based",
        "google", "microsoft", "amazon", "meta", "apple", "netflix"  # ✅ Added specific companies
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