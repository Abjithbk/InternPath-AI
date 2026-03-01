import React, { useEffect, useState } from "react";
import api from "../axios";
import { toast } from "react-toastify";
import MovingNotice from "../component/MovingNotice.jsx";
import { useContext } from "react";
import { UserContext } from "../context/UserContext.jsx";


const Dashboard = () => {
  const [newSkill, setNewSkill] = useState("");
  const [showSkillInput, setShowSkillInput] = useState(false);

  const [newProject, setNewProject] = useState({
    title: "",
    description: "",
    role: "",
    tech_stack: [],
  });
  const [showProjectForm, setShowProjectForm] = useState(false);

  const [techInput, setTechInput] = useState("");
  const [readinessData,setReadinessData] = useState(null);
  const [showReadinessModal,setShowReadinessModal] = useState(false)
const { user, userProfile, setUserProfile, loading } = useContext(UserContext);
  if (loading || !userProfile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="h-10 w-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }


  useEffect(() => {
    if(user?.id) {
      fetchReadinessSilently();
    }
  },[user])

  const fetchReadinessSilently = async () => {
  try {
    const res = await api.get(`/score/${user.id}`);
    setReadinessData(res.data);
  } catch (err) {
    console.log("Readiness preload failed");
  }
};

  const fetchReadiness = async () => {
    setShowReadinessModal(true);
    if(!readinessData) {

      try {
        const res = await api.get(`/score/${user.id}`);
        setReadinessData(res.data);
      }
      catch(err) {
        toast.error("Failed to fetch readiness score");
      }
    }
  };


  const handleAddSkill = async () => {
    if (!newSkill.trim()) return;

    try {
      const res = await api.put("/profile/", {
        skills: [newSkill],
      });
      setUserProfile((prev) => ({ ...prev, skills: [...prev.skills, newSkill] }));
      setNewSkill("");
      setShowSkillInput(false);
      toast.success("New skills added successfully");
    } catch (err) {
      toast.error("Failed to add skill!");
    }
  };
  const handleAddTech = () => {
    if (!techInput.trim()) return;
    setNewProject((prev) => ({
      ...prev,
      tech_stack: [...prev.tech_stack, techInput],
    }));
    setTechInput("");
  };

  const handleAddProject = async () => {
    if (!newProject.title || !newProject.description) return;

    try {
      await api.put("/profile/", { projects: [newProject] });
      setUserProfile((prev) => ({
        ...prev,
        projects: [...prev.projects, newProject],
      }));
      setNewProject({ title: "", description: "", role: "", tech_stack: [] });
      setTechInput("");
      setShowProjectForm(false);
    } catch (err) {
      console.error(err);
      
    }
  };
  return (
    <div className="min-h-screen bg-[#F5F7FB] px-6 py-10">
      <div className="max-w-7xl mx-auto space-y-10">
        <MovingNotice />

        {/* PROFILE BANNER */}
        <div className="bg-indigo-600 rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between text-white shadow-lg">
          {/* Left */}
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 rounded-full bg-emerald-500 flex items-center justify-center text-3xl font-bold shadow-md">
              {user?.name?.[0]?.toUpperCase()}
            </div>

            <div>
              <h2 className="text-3xl font-semibold">{user?.name || "_"}</h2>
              <p className="text-indigo-100 mt-1">
                {userProfile.year}rd Year &nbsp; • &nbsp; {userProfile.department}
              </p>
            </div>
          </div>

          {/* Right */}
          <div className="bg-white text-gray-800 rounded-xl px-6 py-4 mt-6 md:mt-0 flex items-center gap-6 shadow-md">
            <div>
              <p className="text-sm text-gray-500">
                Internship Readiness Score
              </p>
              <h3 onClick={fetchReadiness} className="text-4xl font-bold text-indigo-600">{readinessData?.percentage_score || ""} %</h3>
            </div>
            {/* <button className="bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-2 rounded-lg font-medium transition">
              Edit UserProfile
            </button> */}
          </div>
        </div>

        {/* GRID SECTION */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* LEFT COLUMN */}
          <div className="space-y-8">
            {/* STATS */}
            <div className="bg-white rounded-xl p-6 shadow-sm space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600">
                  ✈️
                </div>
                <p className="text-gray-700">
                  <span className="font-semibold">12</span> Applications sent
                </p>
              </div>

              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600">
                  💡
                </div>
                <p className="text-gray-700">
                  <span className="font-semibold">{userProfile.skills.length}</span>{" "}
                  Skills added
                </p>
              </div>
            </div>

            {/* ACADEMIC DETAILS */}
            <div className="bg-white rounded-xl p-6 shadow-sm space-y-3">
              <h3 className="text-lg font-semibold text-indigo-600">
                Academic Details
              </h3>

              <p className="text-gray-700">Semester: {userProfile.semester}</p>
              <p className="text-gray-700">College: {userProfile.college}</p>
              <p className="text-gray-700">CGPA: {userProfile.cgpa}</p>
            </div>
          </div>

          {/* RIGHT COLUMN */}
          <div className="lg:col-span-2 space-y-8">
            {/* SKILLS */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-indigo-600">
                  Skills
                </h3>
                <button
                  onClick={() => {
                    setShowSkillInput(!showSkillInput);
                  }}
                  className="text-indigo-600 font-medium cursor-pointer"
                >
                  + Add Skill
                </button>
              </div>

              {showSkillInput && (
                <div className="flex gap-2 mb-4">
                  <input
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleAddSkill();
                    }}
                    type="text"
                    placeholder="Enter new skill"
                    className="border border-gray-300 rounded-lg px-3 py-1 w-full"
                  />
                  <button
                    onClick={handleAddSkill}
                    className="bg-indigo-600 text-white px-4 py-1 rounded-lg"
                  >
                    Add
                  </button>
                </div>
              )}

              <div className="flex flex-wrap gap-3">
                {userProfile.skills.map((skill) => (
                  <span
                    key={skill}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* PROJECTS */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-indigo-600">
                  Projects
                </h3>
                <button
                  onClick={() => {
                    setShowProjectForm(!showProjectForm);
                  }}
                  className="text-indigo-600 font-medium cursor-pointer"
                >
                  + Add Project
                </button>
              </div>
              {showProjectForm && (
                <div className="space-y-3 mb-4 border p-4 rounded-lg">
                  <input
                    type="text"
                    placeholder="Title"
                    value={newProject.title}
                    onChange={(e) =>
                      setNewProject({ ...newProject, title: e.target.value })
                    }
                    className="border border-gray-300 px-3 py-1 rounded-lg w-full"
                  />
                  <input
                    type="text"
                    placeholder="Description"
                    value={newProject.description}
                    onChange={(e) =>
                      setNewProject({
                        ...newProject,
                        description: e.target.value,
                      })
                    }
                    className="border border-gray-300 px-3 py-1 rounded-lg w-full"
                  />

                  

                  <button
                    onClick={handleAddProject}
                    className="bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-2 rounded-lg font-medium transition mt-2"
                  >
                    Save Project
                  </button>
                </div>
              )}

              <div className="space-y-4">
                {(userProfile.projects || []).map((project, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
                  >
                    <h3 className="font-semibold text-lg">{project.title}</h3>
                    <p className="text-gray-600 mt-1">{project.description}</p>
                   
                    
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      {showReadinessModal && readinessData && (
  <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
    <div className="bg-white w-[90%] max-w-3xl rounded-2xl p-8 overflow-y-auto max-h-[90vh]">

      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-indigo-600">
          Internship Readiness Breakdown
        </h2>
        <button
          onClick={() => setShowReadinessModal(false)}
          className="text-gray-500 hover:text-red-500"
        >
          ✕
        </button>
      </div>

      {/* SCORE BREAKDOWN */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>Education Score: {readinessData.education_score}</div>
        <div>Skills Score: {readinessData.skills_score}</div>
        <div>Project Score: {readinessData.project_score}</div>
        <div>Final Score: {readinessData.final_score}</div>
        <div>Readiness Level: {readinessData.readiness_level}</div>
      </div>

      {/* GENERAL FEEDBACK */}
      <h3 className="text-lg font-semibold mb-3">Feedback</h3>
      <div className="space-y-4 mb-6">
        {readinessData.feedback.map((item, index) => (
          <div key={index} className="border p-4 rounded-lg">
            <p className="font-semibold">
              {item.area.toUpperCase()} ({item.severity})
            </p>
            <p className="text-gray-600">{item.summary}</p>
            <ul className="list-disc ml-6 mt-2 text-sm text-gray-600">
              {item.reasons.map((reason, i) => (
                <li key={i}>{reason}</li>
              ))}
            </ul>
            <p className="mt-2 text-indigo-600 font-medium">
              Action: {item.action}
            </p>
          </div>
        ))}
      </div>

      {/* PROJECT FEEDBACK */}
      <h3 className="text-lg font-semibold mb-3">Project Feedback</h3>
      <div className="space-y-4">
        {readinessData.project_feedback.map((proj, index) => (
          <div key={index} className="border p-4 rounded-lg">
            <p className="font-semibold">{proj.project}</p>
            <p className="text-red-500">{proj.severity}</p>
            <ul className="list-disc ml-6 mt-2 text-sm text-gray-600">
              {proj.issues.map((issue, i) => (
                <li key={i}>{issue}</li>
              ))}
            </ul>
            <p className="mt-2 text-indigo-600 font-medium">
              Action: {proj.action}
            </p>
          </div>
        ))}
      </div>

    </div>
  </div>
)}
    </div>
  );
};

export default Dashboard;
