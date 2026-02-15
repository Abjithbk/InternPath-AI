from langgraph.graph import StateGraph,END
from typing import TypedDict
from langchain_ollama import ChatOllama
from .retriever import get_retriever
from .tools import web_search,should_use_web_search

class AgentState(TypedDict):
     input:str
     history: str
     output:str
     user_id:int
     user_profile:str


def truncate_history(history: str, max_exchanges: int = 5) -> str:
    """Keep only last N exchanges to prevent context overflow"""
    if not history:
        return ""
    exchanges = history.split("\nUser: ")
    if len(exchanges) > max_exchanges:
        exchanges = exchanges[-max_exchanges:]
    return "\nUser: ".join(exchanges)



def create_graph():
    llm = ChatOllama(
        model = "llama3.2",
        temperature = 0.4,
        num_predict=350,
        num_ctx=4096
    )
    retriever = get_retriever()

    workflow = StateGraph(AgentState)

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
        try:
            
            user_input = state["input"]
            if not user_input or len(user_input.strip()) == 0:
                return {
                    "output": "Hi! I'm your career mentor. Ask me about internships, placements, skills, or career advice!",
                    "history": state.get("history", "")
                } #fallback for first msg,change according to your use


            user_input = user_input.strip()[:500] #limiting length  
            chat_history = state.get("history","")

            chat_history = truncate_history(chat_history, max_exchanges=5) #truncate old history 

            docs = retriever.invoke(user_input)
            rag_context = "\n".join([doc.page_content for doc in docs])
            web_context = ""
            if should_use_web_search(user_input):
                try:
                    search_results = web_search.invoke(user_input)
                    web_context = f"\n\nCurrent Web Information:\n{search_results}"
                except Exception as e:
                    print(f"Web search failed: {e}")
                    web_context = ""

            prompt = f"""You are an expert career mentor AI specializing in internships, placements, and tech careers.
        user_input = state["input"]
        chat_history = state.get("history","")
        user_profile = state.get("user_profile", "User Profile: Not available")

        docs = retriever.invoke(user_input)
        rag_context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""You are an expert career mentor AI providing PERSONALIZED advice.
{user_profile}

Previous conversation:
{chat_history if chat_history else "This is the start of the conversation."}

Knowledge base (roadmaps and guides):
{rag_context}
{web_context}

User question: {user_input}

Instructions:
- If web information is provided, use it for current data (salaries, hiring trends, company info)
- Combine web data with knowledge base for comprehensive advice
- Be specific and actionable
- End with ONE relevant follow-up question

Response:"""
                    
            response = llm.invoke(prompt)
            
            if hasattr(response,'content'):
                response_text = response.content
            else:
                response_text = str(response)

             # Validate response
            if not response_text or len(response_text.strip()) < 10:
                response_text = "I couldn't generate a proper response. Could you rephrase your question?"


            new_history = f"{chat_history}\nUser: {user_input}\nAssistant: {response_text}" #update history
            return {
                "output": response_text,
   
                "history": new_history} #persistent convo
        except Exception as e:
            print(f"Error in mentor_node: {e}")  
            return {
                "output": "I'm having trouble processing that. Could you rephrase your question?",
                "history": state.get("history", "")
            }
    workflow.add_node("mentor",mentor_node)
    workflow.set_entry_point("mentor")
    workflow.add_edge("mentor",END)

    return workflow.compile()

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


