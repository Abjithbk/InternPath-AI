from langgraph.graph import StateGraph,END
from typing import TypedDict
from langchain_ollama import ChatOllama
from .retriever import get_retriever
from .tools import web_search
from database.models import UserProfile,User

class AgentState(TypedDict):
     input:str
     history: str
     output:str
     user_id:int
     user_profile:str

def create_graph():
    llm = ChatOllama(
        model = "llama3.2",
        temperature = 0.4,
        num_predict=300,
        num_ctx=4096
    )
    retriever = get_retriever()

    worflow = StateGraph(AgentState)

    def fetch_profile_node(state: AgentState):

        from database.database import SessionLocal

        db = SessionLocal()
        try:
            user_id = state.get("user_id")
            user = db.query(User).filter(User.id == user_id).first()
            user_name = user.first_name if user and hasattr(user,'first_name') else user.email.split('@')[0] if user else 'User'
            profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

            if profile:
                profile_text = f"""User Profile:
- Name:{user_name}
- Skills: {profile.skills or 'Not provided'}
- Projects: {profile.projects or 'Not provided'}
"""
            else:
                profile_text = "User Profile : Not available"
            
            return {
                "user_profile":profile_text
            }
        finally:
            db.close()


    def mentor_node(state : AgentState):
        user_input = state["input"]
        chat_history = state.get("history","")
        user_profile = state.get("user_profile", "User Profile: Not available")

        docs = retriever.invoke(user_input)
        rag_context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""You are an expert career mentor AI providing PERSONALIZED advice.
{user_profile}

Previous conversation:
{chat_history}

Relevant roadmap knowledge:
{rag_context}

User question:
{user_input}

Give:
1. Clear structured advice
2. Practical next steps
3. 1 follow-up question

Keep it concise but helpful."""
        
        response = llm.invoke(prompt)

        if hasattr(response,'content'):
            response_text = response.content
        else:
            response_text = str(response)

        return {
            "output": response_text
        }
    worflow.add_node("fetch_profile",fetch_profile_node)
    worflow.add_node("mentor",mentor_node)
    worflow.set_entry_point("fetch_profile")
    worflow.add_edge("fetch_profile","mentor")
    worflow.add_edge("mentor",END)

    return worflow.compile()


