from langgraph.graph import StateGraph,END
from typing import TypedDict
from langchain_community.chat_models import ChatOllama
from .retriever import get_retriever
from .tools import web_search

class AgentState(TypedDict):
     input:str
     history: str
     output:str

def create_graph():
    llm = ChatOllama(
        model = "llama3.2",
        temperature = 0.4,
        num_predict=200,
        num_ctx=2048
    )
    retriever = get_retriever()

    worflow = StateGraph(AgentState)

    def mentor_node(state : AgentState):
        user_input = state["input"]
        chat_history = state.get("history","")

        docs = retriever.invoke(user_input)
        rag_context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""You are an expert career mentor AI.

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
    worflow.add_node("mentor",mentor_node)
    worflow.set_entry_point("mentor")
    worflow.add_edge("mentor",END)

    return worflow.compile()


