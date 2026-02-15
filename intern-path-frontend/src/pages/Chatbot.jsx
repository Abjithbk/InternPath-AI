import React, { useEffect, useRef } from 'react'
import { useState } from "react";
import ChatHeader from '../component/ChatHeader';
import ChatMessage from '../component/ChatMessage';
import ChatInput from '../component/ChatInput';
import api from '../axios'
const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [sessionId,setSessionId] = useState(null)
    const [loading,setLoading] = useState(false)
    const messageEndRef = useRef(null);

    const scrollToBottom = () => {
      messageEndRef.current?.scrollIntoView({behavior : "smooth"})
    };

    useEffect(() => {
      scrollToBottom();
    },[messages])

    const sendMessage = async (userMessage) => {
      if(!userMessage.trim()) return;
      const userMsg = {role : 'user',content: userMessage}
      setMessages(prev => [...prev,userMsg]);
      setLoading(true)

      try {
        const response = await api.post("/ai/chat",{
          message : userMessage,
          session_id:sessionId
        });
        if(!sessionId) {
          setSessionId(response.data.session_id);
        }

        const aiMsg = {role:'ai',content:response.data.response};
        setMessages(prev => [...prev,aiMsg]);
      }
      catch(error) {
        let errorMessage = 'Sorry, I encountered an error. Please try again.';
      
      if (error.response?.status === 401) {
        errorMessage = 'Please login to continue.';
        // Optional: redirect to login
        // window.location.href = '/login';
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error. Please try again later.';
      }
      
      const errorMsg = { role: 'ai', content: errorMessage };
      setMessages(prev => [...prev, errorMsg]);
      }
      finally{
        setLoading(false)
      }
    };

    const startNewChat = () => {
       setMessages([]);
       setSessionId(null)
    };

  return (
     <div className="min-h-screen flex flex-col bg-gray-50">
      <ChatHeader onNewChat = {startNewChat} />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-20">
            <h2 className="text-2xl font-bold mb-2">👋 Hi! I'm your Career Mentor</h2>
            <p>Ask me about internships, placements, skills, or career advice!</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <ChatMessage key={idx} role={msg.role} content={msg.content} />
          ))
        )}
        {
          loading && (
            <ChatMessage role = "ai" content="Thinking..." loading = {true} />
          )
        }
        <div ref={messageEndRef} />
      </div>

      <ChatInput onSend={sendMessage} />
    </div>
  )
}

export default Chatbot
