import React from 'react'

const ProgressBar = ({value}) => {
  return (
    <div className="w-full h-4 bg-white border border-gray-300 rounded-full overflow-hidden">
      <div
        className="h-full bg-indigo-600 transition-all"
        style={{ width: `${value}%` }}
      />
    </div>
  )
}

export default ProgressBar
