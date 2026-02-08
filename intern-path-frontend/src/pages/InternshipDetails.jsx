import React from 'react'
import { MapPin, Building2, AlertTriangle, ArrowLeft } from "lucide-react";
import ProgressBar from "../component/ProgressBar";
import { useLocation, useNavigate, useParams } from 'react-router-dom';

const InternshipDetails = () => {
    const { id } = useParams()
    const location = useLocation();
    const internship = location.state?.internship;
    const navigate = useNavigate()

    if (!internship) {
        return (
            <div className="p-10 text-center text-red-500">
                Data not found. Please go back.
            </div>
        )
    }

    const skillsArray = internship.skills.split(',').map(s => s.trim())

    return (
        <div className="min-h-screen bg-[#F5F7FA] px-6 md:px-20 py-8">
            {/* Back Button */}
            <button
                onClick={() => navigate(-1, { replace: true })}
                className="
                    flex items-center gap-2 mb-6
                    text-[#4B50C6] font-medium
                    hover:text-[#3C3F8C] transition
                "
            >
                <ArrowLeft className="w-5 h-5" />
                Back to Internships
            </button>

            {/* Header Section */}
            <div className="mb-8">
                <h1 className="text-3xl md:text-4xl font-bold text-[#2E3A59] mb-4 capitalize">
                    {internship.title}
                </h1>

                <div className="flex flex-wrap items-center gap-6 text-[#5A6C7D]">
                    <span className="flex items-center gap-2">
                        <Building2 className="w-5 h-5" />
                        <span className="font-medium capitalize">{internship.company}</span>
                    </span>
                    <span className="flex items-center gap-2">
                        <MapPin className="w-5 h-5" />
                        <span className='capitalize'>{internship.location}</span>
                    </span>
                </div>
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* LEFT COLUMN - 2/3 width */}
                <div className="lg:col-span-2 space-y-6">

                    {/* Required Skills */}
                    <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
                        <h2 className="text-xl font-semibold text-[#2E3A59] mb-5">
                            Required skills
                        </h2>

                        <div className="flex gap-3 flex-wrap">
                            {skillsArray.map((skill, index) => (
                                <span
                                    key={index}
                                    className="px-5 py-2 bg-[#E8EAF6] text-[#3C3F8C] rounded-lg text-sm font-medium"
                                >
                                    {skill}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Internship Details */}
                    <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
                        <h2 className="text-xl font-semibold text-[#2E3A59] mb-5">
                            Internship Details
                        </h2>

                        <div className="space-y-3 text-[#5A6C7D]">
                            <p className="flex items-center gap-2">
                                <span className="text-xl">💰</span>
                                <span className="font-medium">Stipend :</span>
                                <span className="font-semibold text-[#2E3A59]">{internship.stipend}</span>
                            </p>
                            <p className="flex items-center gap-2">
                                <span className="text-xl">⏳</span>
                                <span className="font-medium">Duration :</span>
                                <span className="font-semibold text-[#2E3A59]">{internship.duration}</span>
                            </p>
                        </div>
                    </div>

                    {/* Students Like You Got Selected */}
                    <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
                        <h2 className="text-xl font-semibold text-[#2E3A59] mb-5">
                            Students Like You Got Selected
                        </h2>

                        <div className="space-y-4">
                            {[
                                { name: "Backend Intern (Java)", percentage: "72%" },
                                { name: "Web developer intern", percentage: "64%" },
                                { name: "Junior Software Intern", percentage: "58%" }
                            ].map((item, index) => (
                                <div key={index} className="flex justify-between items-center text-[#5A6C7D]">
                                    <span className="font-medium">{item.name}</span>
                                    <span className="font-semibold text-[#2E3A59]">{item.percentage}</span>
                                </div>
                            ))}
                        </div>

                        <p className="text-sm text-gray-500 mt-6 leading-relaxed">
                            Based on students with similar skills, resume score, and projects.
                        </p>
                    </div>
                </div>

                {/* RIGHT COLUMN - 1/3 width */}
                <div className="space-y-6">

                    {/* Your Eligibility */}
                    <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 sticky top-6">
                        <h2 className="text-xl font-semibold text-[#2E3A59] mb-6">
                            Your eligibility
                        </h2>

                        {/* Skill Match */}
                        <div className="mb-6">
                            <p className="text-sm font-medium text-[#5A6C7D] mb-3">
                                Skill Match
                            </p>
                            <ProgressBar value={78} />
                            <p className="text-sm font-semibold text-[#2E3A59] mt-2">
                                78% Match
                            </p>
                        </div>

                        {/* Resume Quality */}
                        <div className="mb-6">
                            <p className="text-sm font-medium text-[#5A6C7D] mb-3">
                                Resume Quality
                            </p>
                            <ProgressBar value={65} />
                            <p className="text-sm font-semibold text-[#2E3A59] mt-2">
                                65/100
                            </p>
                        </div>

                        {/* Missing Skills Alert */}
                        <div className="flex items-start gap-3 p-4 bg-[#FFF9E6] rounded-xl mb-6">
                            <AlertTriangle className="w-5 h-5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
                            <div className="text-sm">
                                <span className="text-[#92400E]">Missing Skills: </span>
                                <span className="font-semibold text-[#92400E]">{internship.skill_gap.join(",") || ""}</span>
                            </div>
                        </div>

                        {/* Apply Button */}
                        <button
                            onClick={() => window.open(internship.link, "_blank")}
                            className="
                                w-full py-4 rounded-xl
                                bg-[#4B50C6] text-white font-semibold text-lg
                                hover:bg-[#3C3F8C] transition-all
                                shadow-lg shadow-indigo-200
                            "
                        >
                            Apply Now
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default InternshipDetails