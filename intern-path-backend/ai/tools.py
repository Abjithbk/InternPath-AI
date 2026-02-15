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