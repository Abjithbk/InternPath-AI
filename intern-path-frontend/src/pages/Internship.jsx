import React, { useEffect, useState } from "react"
import InternshipCard from "../component/InternshipCard"
import { Filter } from "lucide-react"
import api from "../axios"

const Internship = () => {
  const [internships, setInternships] = useState([])
  const [allInternships, setAllInternships] = useState([])
  const [showFilters, setShowFilters] = useState(false)
  const [search, setSearch] = useState("")
  const [domain, setDomain] = useState(null)
  const [recommended,setRecommended] = useState([])
  const [matchMap,setMatchMap] = useState({})
  const [maxMatch, setMaxMatch] = useState(0)


  useEffect(() => {

    const fetchRecommendations = async () => {
  try {
    const res = await api.get("/jobs/recommendation")
    const recommendedData = res.data

    // Create match map
    const map = {}
    recommendedData.forEach((item) => {
      map[item.id] = item.match_percentage
    })
    setMatchMap(map)

    // Calculate maxMatch from all recommendations
    const maxMatchValue = recommendedData.length > 0
      ? Math.max(...recommendedData.map(item => item.match_percentage))
      : 0
    setMaxMatch(maxMatchValue)

    // Sort by match and take top 5
    const top5 = recommendedData
      .sort((a, b) => b.match_percentage - a.match_percentage)
      .slice(0, 5)

    setRecommended(top5)

  } catch (err) {
    console.log(err)
  }
}

    const internshipDetails = async () => {
      try {
        const res = await api.get("/jobs/")
        setInternships(res.data.data)
        console.log(res.data.data);
        
        setAllInternships(res.data.data)
      } catch (err) {
        console.log(err)
      }
    }

    const fetchSearch = async () => {
      try {
        if (search.trim() === "") {
          setInternships(allInternships)
          return
        }
        const res = await api.get("/jobs/search", {
          params: { q: search },
        })
        setInternships(res.data.data)
      } catch (err) {
        console.log(err)
      }
    }

    internshipDetails()
    fetchRecommendations()
    fetchSearch()
    
  }, [search])

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
    <div className="min-h-screen bg-[#F5F7FB] pt-28 pb-12">
      <div className="max-w-7xl mx-auto px-6">
        {/* Title */}
        <h1 className="text-4xl font-bold text-[#3C3F8C] mb-8">
          Internship Opportunities
        </h1>

        {/* Search + Filter */}
        <div className="flex items-center gap-4 mb-12">
          <div className="flex-1 bg-[#EEF2FF] rounded-xl px-5 py-3 flex items-center gap-3">
            🔍
            <input
              type="text"
              placeholder="Search internships by role.."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-transparent outline-none w-full text-sm"
            />
          </div>

          <button
            onClick={() => setShowFilters(true)}
            className="
              flex items-center gap-2
              px-6 py-3 rounded-xl
              bg-[#EEF2FF] text-[#4B50C6]
              font-medium text-sm
              hover:bg-indigo-100 transition
            "
          >
            <Filter className="w-5 h-5" />
            Filters
          </button>
        </div>
        {recommended.length > 0 && (
  <div className="mb-14">
    <h2 className="text-xl font-semibold text-[#3C3F8C] mb-5">
      Recommended for you
    </h2>

    <div className="flex gap-6 overflow-x-auto scrollbar-hide pb-2">
      {recommended.map((item) => (
        <div key={item.id} className="min-w-[320px] flex">
          <InternshipCard
            {...item}
            match={item.match_percentage}
            maxMatch={maxMatch} // color relative to highest match
          />
        </div>
      ))}
    </div>
  </div>
)}



        {/* Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {internships.map((item, index) => (
            <InternshipCard key={index} {...item} match={matchMap[item.id] ?? 0} maxMatch={maxMatch} />
          ))}
        </div>
      </div>

      {/* Filter Modal */}
      {showFilters && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setShowFilters(false)}
          />

          <div className="relative z-10 w-full max-w-md bg-white rounded-2xl p-6 shadow-xl">
            <div className="flex justify-between items-center mb-6">
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
                    px-4 py-3 rounded-xl text-sm font-medium text-left
                    transition
                    ${
                      domain === d.key
                        ? "bg-indigo-600 text-white"
                        : "bg-indigo-50 text-indigo-600 hover:bg-indigo-100"
                    }
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

export default Internship
