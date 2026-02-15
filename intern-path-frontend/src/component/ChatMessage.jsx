import React from 'react';
import { User, Bot } from 'lucide-react'; 

const ChatMessage = ({ role,content,loading }) => {
  
  const isUser = role === "user";

  return (
    <div className={`flex w-full mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
      
      {/* Container for the message bubble */}
      <div className={`flex max-w-[75%] ${isUser ? "flex-row-reverse" : "flex-row"} gap-3`}>
        
        
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? "bg-indigo-600" : "bg-white border"}`}>
           {isUser ? <User className="w-5 h-5 text-white" /> : <img 
          src="/chatbotLogo.png" 
          alt="Mentor Logo" 
          className="w-full h-full object-cover scale-[1.8] translate-y-[-2px]" 
        />}
        </div>

        {/* Message Bubble */}
        <div
          className={`p-3 rounded-2xl shadow-sm text-sm ${
            isUser
              ? "bg-indigo-600 text-white rounded-tr-none"
              : "bg-white text-gray-800 border rounded-tl-none"
          }`}
        >
          {loading ? (
            // Typing indicator
            <div className="flex space-x-2 py-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
            </div>
          ) : (
            // Format text with line breaks
            <div className="whitespace-pre-wrap">
              {content}
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default ChatMessage;