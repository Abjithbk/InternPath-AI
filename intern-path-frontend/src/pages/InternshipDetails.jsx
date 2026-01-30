import React from 'react'
import { MapPin, Building2, AlertTriangle, ArrowLeft } from "lucide-react";
import ProgressBar from "../component/ProgressBar";
import { useLocation,useNavigate,useParams } from 'react-router-dom';
const InternshipDetails = () => {
    const {id} = useParams()
    const location = useLocation();

    const internship = location.state?.internship;
    const navigate = useNavigate()

    if(!internship) {
      return (
        <div className="p-10 text-center text-red-500">
        Data not found. Please go back.
      </div>
      )
    }

    const skillsArray = internship.skills.split(',').map(s => s.trim())
  return (
    <div className="min-h-screen bg-gray-50 px-10 py-8">
      <button
        onClick={() => navigate(-1,{replace:true})}
        className="
          flex items-center gap-2 mb-4
          text-indigo-600 font-medium
          hover:text-indigo-800 transition
        "
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Internships
      </button>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">
        Internship Details – ID {id}
      </h1>
        <h1 className="text-3xl font-bold text-gray-900">
          {internship.title}
        </h1>

        <div className="flex items-center gap-6 mt-2 text-gray-600">
          <span className="flex items-center gap-2">
            <Building2 className="w-4 h-4" />
            {internship.company}
          </span>
          <span className="flex items-center gap-2">
            <MapPin className="w-4 h-4" />
            {internship.location}
          </span>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT SIDE */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Description */}
          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-2">
              Internship Description
            </h2>
            <p className="text-gray-700">
              Work on backend services using Java and Spring Boot. You will
              build REST APIs and collaborate with frontend teams.
            </p>
          </div>

          {/* Skills */}
          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-3">
              Required skills
            </h2>

            <div className="flex gap-2 mb-4 flex-wrap">
              {skillsArray.map((skill,index) => (
                <span
                  key={index}
                  className="px-4 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm"
                >
                  {skill}
                </span>
              ))}
            </div>

            <h3 className="text-md font-semibold mb-2">
              Preferred skills
            </h3>

            <div className="flex gap-2 flex-wrap">
              {["Docker", "MySQL"].map(skill => (
                <span
                  key={skill}
                  className="px-4 py-1 bg-gray-200 text-gray-700 rounded-full text-sm"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Details */}
          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4">
              Internship Details
            </h2>

            <p className="mb-2">💰 <b>Stipend:</b> {internship.stipend}</p>
            <p>⏳ <b>Duration:</b> {internship.duration}</p>
          </div>
        </div>

        {/* RIGHT SIDE */}
        <div className="space-y-6">
          
          {/* Eligibility */}
          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4">
              Your eligibility
            </h2>

            <p className="text-sm mb-2">Skill Match</p>
            <ProgressBar value={70} />

            <p className="text-sm mt-4 mb-2">Resume Quality</p>
            <ProgressBar value={65} />

            <p className="mt-2 text-sm text-gray-700">
              65 / 100
            </p>

            <div className="flex items-center gap-2 mt-3 text-yellow-600">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm">
                Missing Skills: <b>Docker</b>
              </span>
            </div>

            <button
             onClick={() => window.open(internship.link, "_blank")}
              className="
                w-full mt-5 py-3 rounded-lg
                bg-indigo-600 text-white font-semibold
                hover:bg-indigo-700 transition
              "
            >
              Apply Now
            </button>
          </div>

          {/* Similar Students */}
          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4">
              Students Like You Got Selected
            </h2>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Backend Intern (Java)</span>
                <span>72%</span>
              </div>
              <div className="flex justify-between">
                <span>Web developer intern</span>
                <span>64%</span>
              </div>
              <div className="flex justify-between">
                <span>Junior Software Intern</span>
                <span>58%</span>
              </div>
            </div>

            <p className="text-xs text-gray-600 mt-4">
              Based on students with similar skills, resume score,
              and projects.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default InternshipDetails
