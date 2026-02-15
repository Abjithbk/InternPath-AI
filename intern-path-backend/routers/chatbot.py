from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database.database import SessionLocal
from database.models import ChatMessage,ChatSession
from database.schemas import ChatMessageResponse,ChatRequest,ChatResponse,ChatSessionResponse
from ai.graph import create_graph
from dependencies import get_current_user

router = APIRouter(prefix="/ai",tags=["AI Chatbot"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

graph = create_graph()

@router.post("/chat",response_model=ChatResponse)
def chat(req : ChatRequest,db:Session = Depends(get_db),current_user = Depends(get_current_user)):

    try:
        user_id = current_user.id
        if not req.session_id:
            session = ChatSession(user_id = user_id)
            db.add(session)
            db.commit()
            db.refresh(session)
        else:
            session = db.query(ChatSession).filter(
                ChatSession.id == req.session_id,
                ChatSession.user_id == user_id
            ).first()

            if not session:
                raise HTTPException(
                    status_code=404,
                    detail="Session not found or you don't have access"
                )
        user_msg = ChatMessage(
            session_id = session.id,
            role = "user",
            content = req.message
        )

        db.add(user_msg)
        db.commit()

        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.timestamp).all()

        history_text = ""

        for msg in messages[:-1]:
            history_text+=f"{msg.role.upper()} : {msg.content}\n"
        
        result = graph.invoke({
            "input":req.message,
            "history":history_text,
            "user_id":user_id
        })

        ai_response = result["output"]

        ai_msg = ChatMessage(
            session_id = session.id,
            role = "ai",
            content = ai_response
        )

        db.add(ai_msg)
        db.commit()
        db.refresh(ai_msg)

        return ChatResponse(
            session_id=session.id,
            response=ai_response,
            timestamp=ai_msg.timestamp
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Internal server error : {str(e)}")
    
@router.get("/session",response_model=List[ChatSessionResponse])
def get_my_session(
    db:Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    
    user_id = current_user.id

    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).order_by(ChatSession.created_at.desc()).all()

    return sessions

@router.get("/session/{session_id}/messages",response_model=List[ChatMessageResponse])

def get_session_messages(
    session_id : int,
    db :Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = current_user.id

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found or you don't have access"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp).all()

    return messages


@router.delete("/session/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ✅ Get logged-in user
):
    """
    Delete a chat session and all its messages
    """
    user_id = current_user.id
    
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id  # ✅ Security check
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=404, 
            detail="Session not found or you don't have access"
        )
    
    # Delete all messages in session
    db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).delete()
    
    # Delete session
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}