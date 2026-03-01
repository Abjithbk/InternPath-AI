from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_groq import ChatGroq
from .retriever import get_retriever
from .tools import web_search, should_use_web_search
from database.models import User, UserProfile
from database.database import SessionLocal
import os


# =========================
# STATE
# =========================
class AgentState(TypedDict):
    input: str
    history: str
    output: str
    user_id: int
    user_profile: str
    web_context: str


# =========================
# UTILITY: TRUNCATE HISTORY
# =========================
def truncate_history(history: str, max_exchanges: int = 4) -> str:
    if not history:
        return ""

    exchanges = history.split("\nUSER: ")
    if len(exchanges) > max_exchanges:
        exchanges = exchanges[-max_exchanges:]

    return "\nUSER: ".join(exchanges)


# =========================
# CREATE GRAPH
# =========================
def create_graph():

    # 🔹 Single LLM (Only one used)
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=250,
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )

    retriever = get_retriever()  # optimized singleton version

    workflow = StateGraph(AgentState)

    # ==========================================
    # NODE 1: FETCH USER PROFILE
    # ==========================================
    def fetch_profile_node(state: AgentState):

        db = SessionLocal()

        try:
            user_id = state.get("user_id")

            user = db.query(User).filter(User.id == user_id).first()
            profile = db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()

            if user:
                user_name = (
                    user.first_name
                    if hasattr(user, "first_name") and user.first_name
                    else user.email.split("@")[0]
                )
            else:
                user_name = "User"

            if profile:
                profile_text = f"""
User Profile:
- Name: {user_name}
- Skills: {profile.skills or 'Not provided'}
- Projects: {profile.projects or 'Not provided'}
"""
            else:
                profile_text = f"""
User Profile:
- Name: {user_name}
- Skills: Not provided
- Projects: Not provided
"""

            return {"user_profile": profile_text}

        except Exception:
            return {"user_profile": "User Profile: Not available"}
        finally:
            db.close()

    # ==========================================
    # NODE 2: OPTIONAL WEB SEARCH
    # ==========================================
    def search_node(state: AgentState):

        user_input = state["input"]

        if not should_use_web_search(user_input):
            return {"web_context": ""}

        try:
            results = web_search(user_input)
            return {"web_context": results[:2000] if results else ""}
        except Exception:
            return {"web_context": ""}

    # ==========================================
    # NODE 3: GENERATE RESPONSE (Single LLM Call)
    # ==========================================
    def mentor_node(state: AgentState):

        user_input = state["input"].strip()[:500]

        if not user_input:
            return {
                "output": "Hi! I'm your career mentor. Ask me about internships, placements, skills, or career advice.",
                "history": state.get("history", ""),
            }

        chat_history = truncate_history(state.get("history", ""), 4)
        user_profile = state.get("user_profile", "")
        web_context = state.get("web_context", "")

        # 🔹 RAG only if no web search
        rag_context = ""
        if not web_context:
            try:
                docs = retriever.invoke(user_input)
                rag_context = "\n".join(
                    [doc.page_content for doc in docs]
                ) if docs else ""
            except Exception:
                rag_context = ""

        prompt = f"""
You are a helpful career mentor AI.

{user_profile}

WEB SEARCH RESULTS:
{web_context if web_context else "None"}

KNOWLEDGE BASE:
{rag_context if rag_context else "General knowledge"}

CONVERSATION HISTORY:
{chat_history if chat_history else "First message"}

USER QUESTION:
{user_input}

INSTRUCTIONS:
- Give a clear, practical answer (3-4 sentences)
- Tailor advice to user's skills/projects
- If web results exist, use them
- If unsure, say honestly
- End with ONE follow-up question

Your response:
"""

        response = llm.invoke(prompt)
        response_text = (
            response.content if hasattr(response, "content") else str(response)
        )

        new_history = f"{chat_history}\nUSER: {user_input}\nAI: {response_text}"

        return {
            "output": response_text,
            "history": new_history,
        }

    # ==========================================
    # BUILD WORKFLOW
    # ==========================================
    workflow.add_node("fetch_profile", fetch_profile_node)
    workflow.add_node("search", search_node)
    workflow.add_node("mentor", mentor_node)

    workflow.set_entry_point("fetch_profile")
    workflow.add_edge("fetch_profile", "search")
    workflow.add_edge("search", "mentor")
    workflow.add_edge("mentor", END)

    print("✅ Optimized graph compiled (Single LLM mode)")

    return workflow.compile()