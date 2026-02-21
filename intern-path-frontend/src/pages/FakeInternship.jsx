import React, { useState } from "react";
import { ShieldCheck,AlertTriangle,ShieldAlert } from "lucide-react";
import api from '../axios';

const FakeInternship = () => {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading,setLoading] = useState(false);
  const [error,setError] = useState("")

  const handleCheck = async () => {
    if(!url) {
      setError("Please enter a url");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null)

    try {
      const response = await api.post("/detect-fake-internship",{
        url
      });
      setResult(response.data);
   
    }
    catch(err) {
      setError("Failed to analyse internship.");
    }
    finally {
      setLoading(false);
    }
  };
   const getColorStyles = () => {
    if (!result) return {};

    if (result.risk_level === "High Risk") {
      return {
        bg: "bg-red-50",
        border: "border-red-500",
        text: "text-red-600",
        icon: <ShieldAlert className="text-red-600 mt-1" />,
      };
    }

    if (result.risk_level === "Medium Risk") {
      return {
        bg: "bg-yellow-50",
        border: "border-yellow-500",
        text: "text-yellow-600",
        icon: <AlertTriangle className="text-yellow-600 mt-1" />,
      };
    }

    return {
      bg: "bg-green-50",
      border: "border-green-500",
      text: "text-green-600",
      icon: <ShieldCheck className="text-green-600 mt-1" />,
    };
  };

  const styles = getColorStyles();

  return (
    <div className="min-h-screen bg-[#EEF2FF] pt-24 px-6">
      <div className="max-w-5xl mx-auto space-y-10">

        {/* HEADER */}
        <div>
          <h1 className="text-3xl font-bold text-indigo-900">
            Fake Internship Checker
          </h1>
          <p className="text-gray-600 mt-2">
            Paste the internship link. We will scan it for suspicious keywords.
          </p>
        </div>

        {/* INPUT CARD */}
        <div className="bg-white rounded-2xl p-8 shadow-sm">
          <label className="block text-indigo-900 font-semibold mb-3">
            Internship URL
          </label>

          <input
            type="text"
            placeholder="https://example.com/internship"
            value={url}
            onChange={(e) => {setUrl(e.target.value)
              setResult(null);
              setError("")
            }}
            className="
              w-full px-4 py-3 rounded-xl
              border-2 border-indigo-500
              focus:outline-none focus:ring-2 focus:ring-indigo-300
            "
          />

          <button
            onClick={handleCheck}
            disabled={!url || loading}
            className={`mt-6 px-6 py-3 rounded-xl text-white font-medium transition
            ${!url || loading 
              ? "bg-gray-400 cursor-not-allowed" 
              : "bg-indigo-600 hover:bg-indigo-700"}
          `}
          >
            { loading ? "Analyzing.." : "Check internship" }
          </button>
          {error && (
            <p className="text-red-500 mt-4">{error}</p>
          )}
        </div>

        {/* RESULT */}
        {result && (
          <div className="bg-white rounded-2xl p-8 shadow-sm">
            <h2 className="text-lg font-semibold text-indigo-900 mb-4">
              Result
            </h2>

            <div className={`flex items-start gap-4 ${styles.bg} border-l-4 ${styles.border} p-6 rounded-xl`}>
              <ShieldCheck className="text-green-600 mt-1" />

              <div>
                <h3 className={`font-semibold ${styles.text} `}>
                  {result.risk_level}
                </h3>
                <ul className="mt-2 text-gray-700 list-disc list-inside">
                  {result.reasons.map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default FakeInternship;
