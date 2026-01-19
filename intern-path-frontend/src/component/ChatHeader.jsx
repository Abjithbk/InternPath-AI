import React from 'react'

const ChatHeader = () => {
  return (
     <div className="flex items-center gap-3 px-8 py-4 bg-indigo-50 border-b">

      <div className="w-10 h-10 rounded-full border border-gray-200 overflow-hidden bg-white flex items-center justify-center shrink-0">
        <img 
          src="/chatbotLogo.png" 
          alt="Mentor Logo" 
          className="w-full h-full object-cover scale-[1.8] translate-y-[-2px]" 
        />
      </div>
      <h1 className="text-xl font-semibold text-gray-800">
        InternPath AI Mentor
      </h1>
    </div>
  )
}

export default ChatHeader
