import React from "react"
import { MapPin } from "lucide-react"
import { useNavigate } from "react-router-dom"

const InternshipCard = ({
  id,
  title,
  company,
  location,
  duration,
  stipend,
  link,
  skills = "",
  skill_gap,
  match=0,
  maxMatch
}) => {
  const navigate = useNavigate()
  const skillsArray = skills.split(",").map((skill) => skill.trim())

  const getMatchStyle = () => {
    const ratio = (match / maxMatch) * 100;
    if (!maxMatch || maxMatch === 0) return "bg-red-100 text-red-700";
    if (ratio >= 85) return "bg-green-100 text-green-700"
    if (ratio >= 70) return "bg-yellow-100 text-yellow-800"
    return "bg-red-100 text-red-700"
  }

  return (
    <div
      onClick={() =>
        navigate(`/Internship/${id}`, {
          state: {
            internship: {
              id,
              title,
              company,
              location,
              skills,
              duration,
              stipend,
              skill_gap,
              link,
            },
          },
        })
      }
      className="
        bg-[#F8FAFF]
        rounded-2xl
        border border-[#E2E6F3]
        p-6
        transition-all duration-300
        hover:-translate-y-1 hover:shadow-lg
        cursor-pointer
        flex flex-col
        h-[320px]
        w-full
      "
    >
      {/* Title */}
      <h2 className="text-lg font-semibold text-[#3C3F8C] line-clamp-2 h-14 capitalize" >
        {title}
      </h2>

      {/* Company */}
      <p className="text-sm text-gray-500 mt-1 line-clamp-1 h-5 capitalize">
        {company}
      </p>

      {/* Location */}
      <div className="flex items-center gap-2 text-sm text-gray-600 mt-3 h-5">
        <MapPin className="w-4 h-4 text-indigo-500 flex-shrink-0" />
        <span className="truncate capitalize">{location}</span>
      </div>

      {/* Skills */}
      <div className="flex flex-wrap gap-2 mt-4 h-16 overflow-hidden content-start">
        {skillsArray.slice(0, 4).map((skill, index) => (
          <span
            key={index}
            className="
              bg-[#E9EDFF]
              text-[#4B50C6]
              text-xs
              px-3 py-1
              rounded-full
              h-fit
            "
          >
            {skill}
          </span>
        ))}
      </div>

      {/* Spacer */}
      <div className="flex-grow"></div>

      {/* Bottom */}
      <div className="flex items-center justify-between pt-4">
        <span
          className={`
            px-4 py-2 rounded-xl text-sm font-medium
            ${getMatchStyle()}
          `}
        >
          {match}% Match
        </span>

        <button
          onClick={(e) => e.stopPropagation()}
          className="
            bg-[#4B50C6]
            text-white
            px-6 py-2
            rounded-xl
            font-medium
            hover:bg-indigo-700
            transition
          "
        >
          Apply
        </button>
      </div>
    </div>
  )
}

export default InternshipCard