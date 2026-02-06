import React, { useEffect, useState } from 'react'
import InternshipCard from '../component/InternshipCard'
import { Filter } from 'lucide-react'
import api from '../axios'

const internship = () => {
     
  const [internships,setInternships] = useState([])
  const [allInternships,setAllInternships] = useState([])
  const [showFilters,setShowFilters] = useState(false)
  const [search,setSearch] = useState("")
  const [domain,setDomain] = useState(null)
   useEffect( () => {
    const internshipDetails = async () => {
      try {
        const res = await api.get("/jobs/");
        console.log(res.data.data);
        setInternships(res.data.data);
        setAllInternships(res.data.data)
      }
      catch(err) {
        console.log(err);
      }
   }
    const fetchSearch = async () => {
     try {
      if(search.trim() === "") {
        setInternships(allInternships)
        return;
      }
      const res = await api.get("/jobs/search",{
        params : {
          q:search
        }
      })
      setInternships(res.data.data);
     }
     catch(err) {
      console.log(err);
     }
    }
    internshipDetails()
    fetchSearch()
   },[search])

  
   const fetchByDomain = async (selectedDomain) => {
      try {
        if (domain === selectedDomain) {
        setDomain(null)
        setInternships(allInternships)
        return
      }
        setDomain(selectedDomain)
        const res = await api.get(`/jobs/filter?domain=${selectedDomain}`)
        setInternships(res.data.data)
      } catch (err) {
        console.error(err)
      }
}


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
            placeholder="Search internships"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
            }}
            className="
              w-full px-4 py-3 rounded-lg border border-gray-200
              focus:outline-none focus:ring-2 focus:ring-indigo-500
            "
          />
        </div>

        <button
        onClick={() => {
          setShowFilters(prev => !prev);
        }}
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

      </div>
      {showFilters && (
  <div className="fixed inset-0 z-50 flex items-center justify-center">
    
    {/* Background Blur */}
    <div
      className="absolute inset-0 bg-black/40 backdrop-blur-sm"
      onClick={() => setShowFilters(false)}
    />

    {/* Filter Modal */}
    <div
      className="
        relative z-10 w-full max-w-md bg-white rounded-xl
        p-6 shadow-xl
        transform transition-all duration-300
        scale-100 opacity-100
      "
    >
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Filter by Domain
        </h2>
        <button
          onClick={() => setShowFilters(false)}
          className="text-gray-400 hover:text-gray-600 text-xl"
        >
          ✕
        </button>
      </div>

      {/* Domain Buttons - Vertical */}
      <div className="flex flex-col gap-3">
        {[
          { key: "ai", label: "Artificial Intelligence" },
          { key: "web", label: "Web Development" },
          { key: "data", label: "Data Science" },
          { key: "mobile", label: "Mobile Development" },
        ].map((d) => (
          <button
            key={d.key}
            onClick={() => {
              fetchByDomain(d.key)
              setShowFilters(false)
            }}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium text-left
              ${domain === d.key
                ? "bg-indigo-600 text-white"
                : "bg-indigo-50 text-indigo-600 hover:bg-indigo-100"}
            `}
          >
            {d.label}
          </button>
        ))}
      </div>
    </div>
  </div>
)}


    </div>
  )
}

export default internship
