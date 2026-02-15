from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_community.chat_models import ChatOllama
from .retriever import get_retriever
from .tools import web_search, should_use_web_search
from database.models import User, UserProfile
import traceback

class AgentState(TypedDict):
    input: str
    history: str
    output: str
    user_id: int
    user_profile: str

def truncate_history(history: str, max_exchanges: int = 5) -> str:
    """Keep only last N exchanges to prevent context overflow"""
    if not history:
        return ""
    exchanges = history.split("\nUSER: ")
    if len(exchanges) > max_exchanges:
        exchanges = exchanges[-max_exchanges:]
    return "\nUSER: ".join(exchanges)

def create_graph():
    llm = ChatOllama(
        model="llama3.2",
        temperature=0.3,  # Lower for more focused responses
        num_predict=400,
        num_ctx=4096,
        repeat_penalty=1.2
    )
    retriever = get_retriever()

    workflow = StateGraph(AgentState)

    # Node 1: Fetch user profile
    def fetch_profile_node(state: AgentState):
        print("\n" + "="*50)
        print("🔵 FETCH PROFILE NODE")
        print("="*50)
        
        from database.database import SessionLocal

        db = SessionLocal()
        try:
            user_id = state.get("user_id")
            print(f"📋 User ID: {user_id}")
            
            # Get user name
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_name = user.first_name if hasattr(user, 'first_name') and user.first_name else user.email.split('@')[0]
                print(f"👤 User found: {user_name}")
            else:
                user_name = 'User'
                print(f"⚠️ User not found, using default name")
            
            # Get profile
            profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

            if profile:
                print(f"✅ Profile found - Skills: {profile.skills}, Projects: {profile.projects}")
                profile_text = f"""User Profile:
- Name: {user_name}
- Skills: {profile.skills or 'Not provided'}
- Projects: {profile.projects or 'Not provided'}
"""
            else:
                print(f"⚠️ No profile found for user")
                profile_text = f"""User Profile:
- Name: {user_name}
- Skills: Not provided
- Projects: Not provided
"""
            
            print(f"📤 Profile text prepared")
            return {"user_profile": profile_text}
        except Exception as e:
            print(f"❌ Error in fetch_profile_node: {e}")
            traceback.print_exc()
            return {"user_profile": "User Profile: Error loading profile"}
        finally:
            db.close()

    # Node 2: Generate mentor response
    def mentor_node(state: AgentState):
        print("\n" + "="*50)
        print("🟢 MENTOR NODE")
        print("="*50)
        
        try:
            user_input = state["input"]
            print(f"📝 User input: '{user_input}'")
            
            # Handle empty input
            if not user_input or len(user_input.strip()) == 0:
                print("⚠️ Empty input detected")
                return {
                    "output": "Hi! I'm your career mentor. Ask me about internships, placements, skills, or career advice!",
                    "history": state.get("history", "")
                }

            # Limit input length
            user_input = user_input.strip()[:500]
            
            # Get history and truncate
            chat_history = state.get("history", "")
            chat_history = truncate_history(chat_history, max_exchanges=5)
            print(f"📜 Chat history length: {len(chat_history)} chars")
            
            # Get user profile
            user_profile = state.get("user_profile", "User Profile: Not available")
            print(f"👤 User profile: {user_profile[:100]}...")

            # RAG - Get relevant documents
            print(f"🔍 Fetching relevant documents from vector DB...")
            try:
                docs = retriever.invoke(user_input)
                rag_context = "\n".join([doc.page_content for doc in docs]) if docs else "No relevant documents found"
                print(f"✅ Retrieved {len(docs)} documents, context length: {len(rag_context)} chars")
            except Exception as e:
                print(f"❌ RAG retrieval failed: {e}")
                rag_context = "Knowledge base unavailable"

            # Web Search Integration
            web_context = ""
            search_triggered = should_use_web_search(user_input)
            print(f"🌐 Web search check: {search_triggered}")
            
            if search_triggered:
                try:
                    print(f"🔍 Performing web search for: '{user_input}'")
                    search_results = web_search.invoke({"query": user_input})
                    print(f"✅ Web search successful, results length: {len(search_results)} chars")
                    print(f"📄 First 200 chars: {search_results[:200]}...")
                    web_context = f"\n\n**CURRENT WEB SEARCH RESULTS (PRIORITIZE THIS):**\n{search_results}\n**END OF WEB RESULTS**\n"
                except Exception as e:
                    print(f"❌ Web search failed: {e}")
                    traceback.print_exc()
                    web_context = ""
            else:
                print(f"⏭️ Skipping web search")

            # Build prompt based on whether we have web results
            if web_context:
                print(f"📝 Building prompt with WEB SEARCH results")
                prompt = f"""You are a career mentor AI. The user is asking about CURRENT information.

{user_profile}

**USER'S EXACT QUESTION:** 
{user_input}

{web_context}

**CRITICAL INSTRUCTIONS:**
1. Answer the user's EXACT question using the web search results above
2. DO NOT ignore their question
3. DO NOT give generic unrelated advice
4. Be specific and cite information from the web results
5. Keep response to 3-4 sentences
6. End with ONE relevant follow-up question

Previous conversation (for context only, don't focus on this):
{chat_history if chat_history else "First message"}

Your response:"""
            else:
                print(f"📝 Building prompt with KNOWLEDGE BASE only")
                prompt = f"""You are a career mentor AI providing personalized advice.

{user_profile}

Previous conversation:
{chat_history if chat_history else "This is the start of the conversation."}

Knowledge base:
{rag_context}

User question:
{user_input}

Instructions:
1. Answer their question directly
2. Tailor advice to their skills and projects
3. Be specific and actionable
4. Keep it 3-4 sentences
5. End with ONE relevant follow-up question

Your response:"""
            
            print(f"📤 Sending prompt to LLM (length: {len(prompt)} chars)")
            
            # Get AI response
            response = llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)

            print(f"📥 LLM response received (length: {len(response_text)} chars)")
            print(f"📄 Response preview: {response_text[:150]}...")

            # Validate response
            if not response_text or len(response_text.strip()) < 10:
                print(f"⚠️ Invalid response, using fallback")
                response_text = "I couldn't generate a proper response. Could you rephrase your question?"

            # Update history
            new_history = f"{chat_history}\nUSER: {user_input}\nAI: {response_text}"
            
            print(f"✅ Mentor node completed successfully")
            return {
                "output": response_text,
                "history": new_history
            }
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR in mentor_node: {e}")
            traceback.print_exc()
            return {
                "output": "I'm having trouble processing that. Could you rephrase your question?",
                "history": state.get("history", "")
            }

    # Add nodes to workflow
    workflow.add_node("fetch_profile", fetch_profile_node)
    workflow.add_node("mentor", mentor_node)
    
    # Set flow
    workflow.set_entry_point("fetch_profile")
    workflow.add_edge("fetch_profile", "mentor")
    workflow.add_edge("mentor", END)

    print("✅ Graph compiled successfully")
    return workflow.compile()
