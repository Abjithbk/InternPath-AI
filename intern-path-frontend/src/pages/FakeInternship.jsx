import React, { useState } from "react";
import { ShieldCheck } from "lucide-react";

const FakeInternship = () => {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);

  const handleCheck = () => {
    // temporary mock result
    setResult({
      level: "Low Risk",
      message:
        "No major red flags detected. This internship looks safe.",
    });
  };

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
            onChange={(e) => setUrl(e.target.value)}
            className="
              w-full px-4 py-3 rounded-xl
              border-2 border-indigo-500
              focus:outline-none focus:ring-2 focus:ring-indigo-300
            "
          />

          <button
            onClick={handleCheck}
            className="
              mt-6 bg-indigo-600 hover:bg-indigo-700
              text-white font-medium
              px-6 py-3 rounded-xl
              transition
            "
          >
            Check internship
          </button>
        </div>

        {/* RESULT */}
        {result && (
          <div className="bg-white rounded-2xl p-8 shadow-sm">
            <h2 className="text-lg font-semibold text-indigo-900 mb-4">
              Result
            </h2>

            <div className="flex items-start gap-4 bg-green-50 border-l-4 border-green-500 p-6 rounded-xl">
              <ShieldCheck className="text-green-600 mt-1" />

              <div>
                <h3 className="font-semibold text-gray-900">
                  {result.level}
                </h3>
                <p className="text-gray-600 mt-1">
                  {result.message}
                </p>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default FakeInternship;
