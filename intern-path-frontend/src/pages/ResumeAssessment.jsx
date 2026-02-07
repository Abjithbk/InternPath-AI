import React from "react";
import { CheckCircle, XCircle, Upload } from "lucide-react";

const sections = [
  { name: "Skills", value: 90, color: "bg-emerald-500" },
  { name: "Projects", value: 70, color: "bg-amber-400" },
  { name: "Education", value: 95, color: "bg-emerald-500" },
  { name: "Formatting & ATS Friendly", value: 50, color: "bg-red-500" },
];

const ResumeAssessment = () => {
  return (
    <div className="min-h-screen bg-[#EEF2FF] pt-24 px-6">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* HEADER */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-semibold text-indigo-900">
            Resume Quality Assessment
          </h1>

          <button className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-xl font-medium shadow">
            <Upload size={18} />
            Upload Resume
          </button>
        </div>

        {/* SCORE + SECTION */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* SCORE CARD */}
          <div className="bg-white rounded-2xl p-8 shadow-sm flex flex-col items-center justify-center">
            <h2 className="text-lg font-semibold text-indigo-900 mb-6">
              Resume Quality Score
            </h2>

            {/* CIRCLE */}
            <div className="relative w-44 h-44 rounded-full bg-emerald-200 flex items-center justify-center">
              <div className="absolute inset-4 rounded-full bg-emerald-500 flex items-center justify-center">
                <span className="text-4xl font-bold text-white">82%</span>
              </div>
            </div>

            <p className="mt-6 text-emerald-600 font-semibold text-lg">
              Strong Resume
            </p>
          </div>

          {/* SECTION EVALUATION */}
          <div className="lg:col-span-2 bg-white rounded-2xl p-8 shadow-sm">
            <h2 className="text-lg font-semibold text-indigo-900 mb-6">
              Section-wise Evaluation
            </h2>

            <div className="space-y-6">
              {sections.map((sec) => (
                <div key={sec.name}>
                  <div className="flex justify-between text-sm font-medium text-indigo-900 mb-2">
                    <span>{sec.name}</span>
                    <span>{sec.value}%</span>
                  </div>

                  <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${sec.color} rounded-full`}
                      style={{ width: `${sec.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* SKILL MATCH */}
        <div className="bg-white rounded-2xl p-8 shadow-sm">
          <h2 className="text-lg font-semibold text-indigo-900 mb-6">
            Skill Match with Internships
          </h2>

          <div className="space-y-4">
            <div className="flex items-center gap-3 text-gray-800">
              <CheckCircle className="text-emerald-500" />
              <span className="font-medium">Python</span>
            </div>

            <div className="flex items-center gap-3 text-gray-800">
              <CheckCircle className="text-emerald-500" />
              <span className="font-medium">Django</span>
            </div>

            <div className="flex items-center gap-3 text-gray-800">
              <XCircle className="text-red-500" />
              <span className="font-medium">Docker</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ResumeAssessment;
