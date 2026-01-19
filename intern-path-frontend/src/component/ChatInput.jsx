import React from 'react'
import { Send } from "lucide-react";
import { useState } from "react";
const ChatInput = ({onSend}) => {
    const [message, setMessage] = useState("");

  const handleSend = () => {
    if (!message.trim()) return;
    onSend(message);
    setMessage("");
  };
  return (
    <div className="flex items-center gap-4 px-6 py-4 bg-white border-t">
      <input
        type="text"
        placeholder="Ask about internships, skills, resume tips..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        className="flex-1 px-5 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />

      <button
        onClick={handleSend}
        className="bg-gray-900 text-white p-4 rounded-full hover:bg-gray-800 transition"
      >
        <Send className="w-5 h-5" />
      </button>
    </div>
  )
}

export default ChatInput
