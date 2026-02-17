import React, { useState } from 'react'
import { Send } from 'lucide-react'

const ChatInput = ({ onSend, disabled }) => {
  const [message, setMessage] = useState('')

  const handleSend = () => {
    if (!message.trim() || disabled) return
    onSend(message)
    setMessage('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="px-8 py-5 bg-transparent">
      <div className="flex items-center gap-3 bg-white border border-gray-200 rounded-full px-5 py-3 shadow-md focus-within:ring-2 focus-within:ring-indigo-300 focus-within:border-indigo-300 transition-all duration-200">
        <input
          type="text"
          placeholder="Ask about internships, skills, resume tips..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={disabled}
          className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 focus:outline-none disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className="bg-gray-900 text-white p-2.5 rounded-full hover:bg-gray-700 active:scale-90 transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

export default ChatInput