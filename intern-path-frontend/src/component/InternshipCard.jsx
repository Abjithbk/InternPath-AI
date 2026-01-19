import React from 'react'
import { MapPin } from "lucide-react";
import { useNavigate } from 'react-router-dom';

const InternshipCard = ({ id,title,company,location,tags,match,matchColor,}) => {
  const navigate = useNavigate()
  return (
     <div onClick={() => {
        navigate(`/Internship/${id}`);
     }}
      className="
        bg-white rounded-xl border border-gray-200
        p-6 w-full max-w-md
        transition-all duration-300 ease-in-out
        hover:scale-[1.03] hover:shadow-xl
        cursor-pointer
      "
    >
      <h2 className="text-lg font-semibold text-gray-900">
        {title}
      </h2>

      <p className="text-sm text-gray-500 mt-1">
        {company}
      </p>

      <div className="flex items-center gap-2 text-sm text-gray-600 mt-3">
        <MapPin className="w-4 h-4 text-indigo-500" />
        <span>{location}</span>
      </div>

      <div className="flex flex-wrap gap-2 mt-4">
        {tags.map((tag, index) => (
          <span
            key={index}
            className="px-3 py-1 text-xs bg-indigo-50 text-indigo-600 rounded-full"
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between mt-6">
        <span
          className={`px-4 py-2 text-sm font-medium rounded-lg ${matchColor}`}
        >
          {match}% Match
        </span>

        <button
          className="
            bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium
            hover:bg-indigo-700 transition
          "
        >
          Apply
        </button>
      </div>
    </div>
  )
}

export default InternshipCard
