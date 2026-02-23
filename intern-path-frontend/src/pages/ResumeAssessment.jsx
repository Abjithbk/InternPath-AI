import React, { useState } from "react";
import { CheckCircle, XCircle, Upload,Loader } from "lucide-react";
import api from '../axios'
const gradeColor = (grade) => {
  if (grade === "A") return "text-emerald-600";
  if (grade === "B") return "text-amber-500";
  return "text-red-500";
};

const scoreColor = (value) => {
  if (value >= 80) return "bg-emerald-500";
  if (value >= 50) return "bg-amber-400";
  return "bg-red-500";
};

const scoreLabel = (score) => {
  if (score >= 80) return { text: "Strong Resume", color: "text-emerald-600" };
  if (score >= 60) return { text: "Good Resume", color: "text-amber-500" };
  return { text: "Needs Improvement", color: "text-red-500" };
};

const ResumeAssessment = () => {
  const [result,setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileName, setFileName] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if(!file) return;

    setFileName(file.name);
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file",file);

    try {
      const response = await api.post("/resume/analyze",formData,{
        headers:{
          "Content-Type":"multipart/form-data"
        }
      });
      setResult(response.data);
    }
    catch(err) {
      setError("Failed to analyze resume. Please try again.");
    }
    finally {
      setLoading(false)
    }
  };
  const sections = result
    ? [
        { name: "Skills", value: result.section_scores.skills, color: scoreColor(result.section_scores.skills) },
        { name: "Projects", value: result.section_scores.projects, color: scoreColor(result.section_scores.projects) },
        { name: "Education", value: result.section_scores.education, color: scoreColor(result.section_scores.education) },
        { name: "Formatting & ATS Friendly", value: result.section_scores.ats_formatting, color: scoreColor(result.section_scores.ats_formatting) },
      ]
    : [
        { name: "Skills", value: 0, color: "bg-gray-300" },
        { name: "Projects", value: 0, color: "bg-gray-300" },
        { name: "Education", value: 0, color: "bg-gray-300" },
        { name: "Formatting & ATS Friendly", value: 0, color: "bg-gray-300" },
      ];
      const linguistic = result?.linguistic_features;
      const label = result ? scoreLabel(result.overall_score) : null;

  return (
    <div className="min-h-screen bg-[#F5F7FB] pt-24 px-6">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* HEADER */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-semibold text-indigo-900">
            Resume Quality Assessment
          </h1>

          <label className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-xl font-medium shadow cursor-pointer">
            <Upload size={18} />
            {loading ? "Analyzing..." : "Upload Resume"}
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleUpload}
              disabled={loading}
            />
          </label>
        </div>

        {/* FILE NAME */}
        {fileName && (
          <p className="text-sm text-indigo-700">
            📄 {fileName}
          </p>
        )}

        {/* ERROR */}
        {error && (
          <div className="bg-red-100 text-red-600 px-4 py-3 rounded-xl">
            {error}
          </div>
        )}

        {/* LOADING */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader className="animate-spin text-indigo-500" size={48} />
            <span className="ml-4 text-indigo-700 text-lg font-medium">Analyzing your resume...</span>
          </div>
        )}

        {/* RESULTS */}
        {!loading && (
          <>
            {/* SCORE + SECTION */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

              {/* SCORE CARD */}
              <div className="bg-white rounded-2xl p-8 shadow-sm flex flex-col items-center justify-center">
                <h2 className="text-lg font-semibold text-indigo-900 mb-6">
                  Resume Quality Score
                </h2>

                {/* CIRCLE */}
                <div className="relative w-44 h-44 rounded-full bg-emerald-200 flex items-center justify-center">
                  <div className={`absolute inset-4 rounded-full flex items-center justify-center ${result ? scoreColor(result.overall_score) : "bg-gray-300"}`}>
                    <span className="text-4xl font-bold text-white">
                      {result ? `${result.overall_score}%` : "--"}
                    </span>
                  </div>
                </div>

                {result && (
                  <>
                    <p className={`mt-6 font-semibold text-lg ${label.color}`}>
                      {label.text}
                    </p>
                    <p className={`text-2xl font-bold mt-1 ${gradeColor(result.grade)}`}>
                      Grade: {result.grade}
                    </p>
                  </>
                )}

                {!result && (
                  <p className="mt-6 text-gray-400 text-sm">
                    Upload a resume to see results
                  </p>
                )}
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
                          className={`h-full ${sec.color} rounded-full transition-all duration-700`}
                          style={{ width: `${sec.value}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* LINGUISTIC FEATURES */}
            {linguistic && (
              <div className="bg-white rounded-2xl p-8 shadow-sm">
                <h2 className="text-lg font-semibold text-indigo-900 mb-6">
                  Linguistic Analysis
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {[
                    { label: "Strong Verbs", value: `${(linguistic.strong_verb_ratio * 100).toFixed(1)}%` },
                    { label: "Impact Density", value: `${(linguistic.impact_density * 100).toFixed(1)}%` },
                    { label: "Vocabulary Richness", value: `${(linguistic.unique_lemma_ratio * 100).toFixed(1)}%` },
                    { label: "Avg Sentence Length", value: `${linguistic.avg_sentence_length.toFixed(1)} words` },
                    { label: "Noun Ratio", value: `${(linguistic.noun_ratio * 100).toFixed(1)}%` },
                    { label: "Verb Ratio", value: `${(linguistic.verb_ratio * 100).toFixed(1)}%` },
                    { label: "Passive Voice", value: `${(linguistic.passive_ratio * 100).toFixed(1)}%` },
                    { label: "Entity Density", value: `${(linguistic.entity_density * 100).toFixed(1)}%` },
                  ].map((item) => (
                    <div key={item.label} className="bg-indigo-50 rounded-xl p-4 text-center">
                      <p className="text-2xl font-bold text-indigo-700">{item.value}</p>
                      <p className="text-xs text-indigo-500 mt-1">{item.label}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ResumeAssessment;
