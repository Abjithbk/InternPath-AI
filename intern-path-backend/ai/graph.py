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
    web_context: str
    facts_extracted: str
    needs_regeneration: bool

def truncate_history(history: str, max_exchanges: int = 5) -> str:
    """Keep only last N exchanges to prevent context overflow"""
    if not history:
        return ""
    exchanges = history.split("\nUSER: ")
    if len(exchanges) > max_exchanges:
        exchanges = exchanges[-max_exchanges:]
    return "\nUSER: ".join(exchanges)

def create_graph():
    # Main LLM for responses
    llm = ChatOllama(
        model="llama3.2",
        temperature=0.1,  # Lower for more factual responses
        num_predict=400,
        num_ctx=4096,
        repeat_penalty=1.3,
        top_p=0.9,
        top_k=40
    )
    
    # Verification LLM
    verification_llm = ChatOllama(
        model="llama3.2",
        temperature=0.0,  # Zero for strict verification
        num_predict=200
    )
    
    retriever = get_retriever()
    workflow = StateGraph(AgentState)

    # ==========================================
    # NODE 1: FETCH USER PROFILE
    # ==========================================
    def fetch_profile_node(state: AgentState):
        print("\n" + "="*50)
        print("🔵 FETCH PROFILE NODE")
        print("="*50)
        
        from database.database import SessionLocal

        db = SessionLocal()
        try:
            user_id = state.get("user_id")
            print(f"📋 User ID: {user_id}")
            
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_name = user.first_name if hasattr(user, 'first_name') and user.first_name else user.email.split('@')[0]
                print(f"👤 User: {user_name}")
            else:
                user_name = 'User'
                print(f"⚠️ User not found")
            
            profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

            if profile:
                print(f"✅ Profile: Skills={profile.skills}, Projects={profile.projects}")
                profile_text = f"""User Profile:
- Name: {user_name}
- Skills: {profile.skills or 'Not provided'}
- Projects: {profile.projects or 'Not provided'}
"""
            else:
                print(f"⚠️ No profile")
                profile_text = f"""User Profile:
- Name: {user_name}
- Skills: Not provided
- Projects: Not provided
"""
            
            return {"user_profile": profile_text}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"user_profile": "User Profile: Error loading"}
        finally:
            db.close()

    # ==========================================
    # NODE 2: WEB SEARCH & FACT EXTRACTION
    # ==========================================
    def search_and_extract_node(state: AgentState):
        print("\n" + "="*50)
        print("🔍 SEARCH & EXTRACT NODE")
        print("="*50)
        
        user_input = state["input"]
        search_triggered = should_use_web_search(user_input)
        print(f"🌐 Trigger: {search_triggered}")
        
        if not search_triggered:
            return {"web_context": "", "facts_extracted": ""}
        
        try:
            print(f"🔍 Searching: '{user_input}'")
            search_results = web_search.invoke({"query": user_input})
            
            if not search_results or len(search_results.strip()) < 50:
                print("⚠️ No results")
                return {"web_context": "", "facts_extracted": ""}
            
            print(f"✅ Got {len(search_results)} chars")
            
            # Extract structured facts
            extract_prompt = f"""You are a fact extraction assistant. Extract ONLY verifiable facts from the web search results.

**WEB SEARCH RESULTS:**
{search_results}

**USER QUESTION:** {user_input}

**INSTRUCTIONS:**
1. Extract 3-5 specific facts that answer the question
2. Include source/website for each fact
3. If no clear answer, state: "INSUFFICIENT_INFORMATION"
4. DO NOT add information not in the search results
5. Format as bullet points

**EXTRACTED FACTS:**"""
            
            print("📝 Extracting facts...")
            facts_response = llm.invoke(extract_prompt)
            facts = facts_response.content if hasattr(facts_response, 'content') else str(facts_response)
            
            if "INSUFFICIENT_INFORMATION" in facts or len(facts.strip()) < 20:
                print("⚠️ No specific facts")
                return {
                    "web_context": search_results,
                    "facts_extracted": "No specific facts found."
                }
            
            print(f"✅ Facts: {facts[:150]}...")
            
            return {
                "web_context": search_results,
                "facts_extracted": facts
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
            return {"web_context": "", "facts_extracted": ""}

    # ==========================================
    # NODE 3: GENERATE RESPONSE
    # ==========================================
    def mentor_node(state: AgentState):
        print("\n" + "="*50)
        print("🟢 MENTOR NODE")
        print("="*50)
        
        try:
            user_input = state["input"]
            print(f"📝 Input: '{user_input}'")
            
            if not user_input or len(user_input.strip()) == 0:
                return {
                    "output": "Hi! I'm your career mentor. Ask me about internships, placements, skills, or career advice!",
                    "history": state.get("history", ""),
                    "needs_regeneration": False
                }

            user_input = user_input.strip()[:500]
            chat_history = truncate_history(state.get("history", ""), max_exchanges=5)
            user_profile = state.get("user_profile", "User Profile: Not available")
            web_context = state.get("web_context", "")
            facts_extracted = state.get("facts_extracted", "")
            
            # RAG only if no web search
            rag_context = ""
            if not web_context:
                print(f"🔍 RAG...")
                try:
                    docs = retriever.invoke(user_input)
                    rag_context = "\n".join([doc.page_content for doc in docs]) if docs else ""
                    print(f"✅ RAG: {len(docs)} docs")
                except Exception as e:
                    print(f"❌ RAG failed: {e}")

            # Build prompt
            if web_context and facts_extracted:
                # STRICT WEB SEARCH MODE
                prompt = f"""You are a precise career mentor AI. Answer using ONLY the extracted facts below.

{user_profile}

**EXTRACTED FACTS (USE ONLY THESE):**
{facts_extracted}

**CRITICAL RULES:**
1. Use ONLY the extracted facts above
2. Cite the specific source
3. If facts don't fully answer, say: "Based on search results, I found [fact], but I don't have complete info about [missing part]."
4. DO NOT use your internal knowledge
5. DO NOT make up information
6. 3-4 sentences max
7. End with ONE follow-up question

**USER QUESTION:** {user_input}

**CONVERSATION HISTORY (context only):**
{chat_history if chat_history else "First message"}

Your response (ONLY use extracted facts, cite sources):"""
            else:
                # KNOWLEDGE BASE MODE
                prompt = f"""You are a career mentor AI.

{user_profile}

**KNOWLEDGE BASE:**
{rag_context if rag_context else "General knowledge"}

**PREVIOUS CONVERSATION:**
{chat_history if chat_history else "First message"}

**USER QUESTION:** {user_input}

**INSTRUCTIONS:**
1. Answer based on knowledge base
2. If no info, say: "I don't have specific information about that."
3. Tailor to user's skills/projects
4. 3-4 sentences
5. End with ONE follow-up question

Your response:"""
            
            print(f"📤 Generating...")
            response = llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)

            print(f"📥 Response: {response_text[:100]}...")

            if not response_text or len(response_text.strip()) < 10:
                response_text = "I couldn't generate a response. Could you rephrase?"
                return {
                    "output": response_text,
                    "history": state.get("history", ""),
                    "needs_regeneration": True
                }

            new_history = f"{chat_history}\nUSER: {user_input}\nAI: {response_text}"
            
            return {
                "output": response_text,
                "history": new_history,
                "needs_regeneration": False
            }
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            traceback.print_exc()
            return {
                "output": "I'm having trouble. Please rephrase.",
                "history": state.get("history", ""),
                "needs_regeneration": True
            }

    # ==========================================
    # NODE 4: VERIFY RESPONSE
    # ==========================================
    def verify_response_node(state: AgentState):
        print("\n" + "="*50)
        print("✅ VERIFICATION NODE")
        print("="*50)
        
        if not state.get("web_context"):
            print("⏭️ No web context, skip")
            return state
        
        if state.get("needs_regeneration"):
            print("⏭️ Already flagged")
            return state
        
        try:
            response = state["output"]
            facts = state.get("facts_extracted", "")
            
            verification_prompt = f"""You are a fact-checker. Verify if the AI response is grounded in the facts.

**EXTRACTED FACTS:**
{facts}

**AI RESPONSE:**
{response}

**TASK:**
1. Check if each claim is supported by facts
2. Identify hallucinations (info not in facts)
3. Rate: "SUPPORTED", "PARTIALLY_SUPPORTED", or "HALLUCINATION"

**RULES:**
- SUPPORTED: All claims in facts
- PARTIALLY_SUPPORTED: Some claims supported
- HALLUCINATION: Contains info NOT in facts

**VERIFICATION:**
List claims and whether supported.
Then rate: RATING: [SUPPORTED/PARTIALLY_SUPPORTED/HALLUCINATION]"""
            
            print("🔍 Verifying...")
            verification_result = verification_llm.invoke(verification_prompt)
            verification_text = verification_result.content if hasattr(verification_result, 'content') else str(verification_result)
            
            print(f"📋 Verification: {verification_text[:150]}...")
            
            if "HALLUCINATION" in verification_text.upper():
                print("❌ HALLUCINATION DETECTED")
                return {
                    **state,
                    "needs_regeneration": True,
                    "output": "I need to search for more specific information to answer accurately."
                }
            elif "PARTIALLY_SUPPORTED" in verification_text.upper():
                print("⚠️ Partially supported")
                return {**state, "needs_regeneration": False}
            else:
                print("✅ Verified")
                return {**state, "needs_regeneration": False}
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return {**state, "needs_regeneration": False}

    # ==========================================
    # NODE 5: REGENERATE IF NEEDED
    # ==========================================
    def regenerate_node(state: AgentState):
        print("\n" + "="*50)
        print("🔄 REGENERATION NODE")
        print("="*50)
        
        user_input = state["input"]
        facts = state.get("facts_extracted", "")
        
        safe_prompt = f"""You are a careful career mentor. The previous response had unsupported info.

**AVAILABLE FACTS:**
{facts if facts else "No facts available"}

**USER QUESTION:** {user_input}

**INSTRUCTIONS:**
1. Answer ONLY with info in facts
2. If insufficient, say: "I found info about [topic], but don't have complete details about [aspect]. Want me to search more?"
3. Be honest about limitations
4. 2-3 sentences max

Your careful response:"""
        
        try:
            response = llm.invoke(safe_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            print(f"✅ Regenerated: {response_text[:100]}...")
            
            chat_history = truncate_history(state.get("history", ""), max_exchanges=5)
            new_history = f"{chat_history}\nUSER: {user_input}\nAI: {response_text}"
            
            return {
                "output": response_text,
                "history": new_history,
                "needs_regeneration": False
            }
        except Exception as e:
            print(f"❌ Regeneration failed: {e}")
            return {
                "output": "I'm unable to provide a verified answer. Could you rephrase?",
                "history": state.get("history", ""),
                "needs_regeneration": False
            }

    # ==========================================
    # BUILD WORKFLOW
    # ==========================================
    workflow.add_node("fetch_profile", fetch_profile_node)
    workflow.add_node("search_and_extract", search_and_extract_node)
    workflow.add_node("mentor", mentor_node)
    workflow.add_node("verify", verify_response_node)
    workflow.add_node("regenerate", regenerate_node)
    
    # Set flow
    workflow.set_entry_point("fetch_profile")
    workflow.add_edge("fetch_profile", "search_and_extract")
    workflow.add_edge("search_and_extract", "mentor")
    workflow.add_edge("mentor", "verify")
    
    # Conditional routing after verification
    def route_verification(state):
        if state.get("needs_regeneration"):
            return "regenerate"
        return END
    
    workflow.add_conditional_edges(
        "verify",
        route_verification,
        {
            "regenerate": "regenerate",
            END: END
        }
    )
    
    workflow.add_edge("regenerate", END)

    print("✅ Graph compiled with anti-hallucination")
    return workflow.compile()