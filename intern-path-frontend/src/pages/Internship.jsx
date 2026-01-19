import React from 'react'
import InternshipCard from '../component/InternshipCard'
import { Filter } from 'lucide-react'

const internship = () => {
     const internships = [
    {
      id:1,
      title: "Backend Developer intern",
      company: "TechNova",
      location: "Remote",
      tags: ["Java", "Spring Boot", "Rest API"],
      match: 63,
      matchColor: "bg-red-100 text-red-600",
    },
    {
      id:2,
      title: "Frontend Developer intern",
      company: "PixelWorks",
      location: "Bangalore",
      tags: ["HTML", "CSS", "React"],
      match: 78,
      matchColor: "bg-yellow-100 text-yellow-700",
    },
    {
      id:3,
      title: "Data Science Intern",
      company: "InsightAI",
      location: "Hybrid",
      tags: ["Python", "Pandas", "ML"],
      match: 92,
      matchColor: "bg-green-100 text-green-700",
    },
  ]

  return (
     <div  className="min-h-screen bg-gray-50 px-8 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Internship Opportunities
      </h1>

      {/* Search & Filter */}
      <div className="flex items-center gap-4 mb-8">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Search internships by role.."
            className="
              w-full px-4 py-3 rounded-lg border border-gray-200
              focus:outline-none focus:ring-2 focus:ring-indigo-500
            "
          />
        </div>

        <button
          className="
            flex items-center gap-2 px-4 py-3
            bg-indigo-50 text-indigo-600
            rounded-lg font-medium
            hover:bg-indigo-100 transition
          "
        >
          <Filter className="w-5 h-5" />
          Filters
        </button>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {internships.map((item, index) => (
          <InternshipCard key={index} {...item} />
        ))}

        {internships.slice(1).map((item, index) => (
          <InternshipCard key={`dup-${index}`} {...item} />
        ))}
      </div>
    </div>
  )
}

export default internship
