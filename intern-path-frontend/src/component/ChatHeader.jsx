import React from 'react'
import { Plus } from 'lucide-react'

const ChatHeader = ({ onNewChat }) => {
  return (
    <div className="flex items-center justify-between px-8 py-4 bg-indigo-50 border-b border-indigo-100 shadow-sm">
      <div className="flex items-center gap-3">
        {/* Robot logo circle */}
        <div className="w-10 h-10 rounded-full border border-gray-200 overflow-hidden bg-white flex items-center justify-center shrink-0 shadow-sm">
          <img
            src="/chatbotLogo.png"
            alt="Mentor Logo"
            className="w-full h-full object-cover scale-[1.8] translate-y-[-2px]"
          />
        </div>
        <h1 className="text-xl font-semibold text-gray-800 tracking-tight">
          InternPath AI Mentor
        </h1>
      </div>

      {/* New Chat Button */}
      <button
        onClick={onNewChat}
        className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 active:scale-95 transition-all duration-150 text-sm font-medium shadow-md"
      >
        <Plus className="w-4 h-4" />
        New Chat
      </button>
    </div>
  )
}

export default ChatHeader