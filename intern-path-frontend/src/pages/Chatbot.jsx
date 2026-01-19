import React from 'react'
import { useState } from "react";
import ChatHeader from '../component/ChatHeader';
import ChatMessage from '../component/ChatMessage';
import ChatInput from '../component/ChatInput';
const Chatbot = () => {
    const [messages, setMessages] = useState([
    {
      text: "Hello 👋, I’m your AI internship Mentor. Ask me anything about internships, skills, or resumes",
      sender: "bot",
    },
  ]);

  const handleSend = (msg) => {
    setMessages((prev) => [
      
      ...prev,
      { text: msg, sender: "user" },
      {
        text: "That’s a great question. Based on your profile, focusing on practical projects and improving core skills will increase your chances.",
        sender: "bot",
      },
    ]);
  };

  return (
     <div className="min-h-screen flex flex-col bg-gray-50">
      <ChatHeader />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {messages.map((msg, index) => (
          <ChatMessage
            key={index}
            text={msg.text}
            sender={msg.sender}
          />
        ))}
      </div>

      <ChatInput onSend={handleSend} />
    </div>
  )
}

export default Chatbot
