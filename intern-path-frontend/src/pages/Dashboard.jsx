import React, { useEffect, useState } from "react";
import api from "../axios";
import { useContext } from "react";
import { UserContext } from "../context/UserContext.jsx";
import { toast } from "react-toastify";
import MovingNotice from "../component/MovingNotice.jsx";

const Dashboard = () => {
  const [profile, setProfile] = useState(null);
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
  const { user, loading } = useContext(UserContext);
  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const res = await api.get("/profile/");
        console.log(res.data);
        setProfile(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchUserProfile();
  }, []);
  if (!profile) {
    return <div className="p-10">Loading...</div>;
  }

  const handleAddSkill = async () => {
    if (!newSkill.trim()) return;

    try {
      const res = await api.put("/profile/", {
        skills: [newSkill],
      });
      setProfile((prev) => ({ ...prev, skills: [...prev.skills, newSkill] }));
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
      setProfile((prev) => ({
        ...prev,
        projects: [...prev.projects, newProject],
      }));
      setNewProject({ title: "", description: "", role: "", tech_stack: [] });
      setTechInput("");
      setShowProjectForm(false);
    } catch (err) {
      console.error(err);
      alert("Failed to add project!");
    }
  };
  return (
    <div className="min-h-screen bg-[#EEF2FF] px-6 py-10">
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
                {profile.year}rd Year &nbsp; • &nbsp; {profile.department}
              </p>
            </div>
          </div>

          {/* Right */}
          <div className="bg-white text-gray-800 rounded-xl px-6 py-4 mt-6 md:mt-0 flex items-center gap-6 shadow-md">
            <div>
              <p className="text-sm text-gray-500">
                Internship Readiness Score
              </p>
              <h3 className="text-4xl font-bold text-indigo-600">82%</h3>
            </div>
            {/* <button className="bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-2 rounded-lg font-medium transition">
              Edit Profile
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
                  <span className="font-semibold">{profile.skills.length}</span>{" "}
                  Skills added
                </p>
              </div>
            </div>

            {/* ACADEMIC DETAILS */}
            <div className="bg-white rounded-xl p-6 shadow-sm space-y-3">
              <h3 className="text-lg font-semibold text-indigo-600">
                Academic Details
              </h3>

              <p className="text-gray-700">Semester: {profile.semester}</p>
              <p className="text-gray-700">College: {profile.college}</p>
              <p className="text-gray-700">CGPA: {profile.cgpa}</p>
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
                {profile.skills.map((skill) => (
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
                  <input
                    type="text"
                    placeholder="Role"
                    value={newProject.role}
                    onChange={(e) =>
                      setNewProject({ ...newProject, role: e.target.value })
                    }
                    className="border border-gray-300 px-3 py-1 rounded-lg w-full"
                  />

                  {/* Tech stack input */}
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Add tech"
                      value={techInput}
                      onChange={(e) => setTechInput(e.target.value)}
                      className="border border-gray-300 px-3 py-1 rounded-lg w-full"
                    />
                    <button
                      onClick={handleAddTech}
                      className="bg-indigo-600 text-white px-4 py-1 rounded-lg"
                    >
                      Add Tech
                    </button>
                  </div>

                  {/* Show current tech stack */}
                  <div className="flex flex-wrap gap-2">
                    {newProject.tech_stack.map((tech, i) => (
                      <span
                        key={i}
                        className="bg-indigo-100 text-indigo-800 px-2 py-1 rounded-full text-sm"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>

                  <button
                    onClick={handleAddProject}
                    className="bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-2 rounded-lg font-medium transition mt-2"
                  >
                    Save Project
                  </button>
                </div>
              )}

              <div className="space-y-4">
                {(profile.projects || []).map((project, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
                  >
                    <h3 className="font-semibold text-lg">{project.title}</h3>
                    <p className="text-gray-600 mt-1">{project.description}</p>
                    <p className="mt-3 text-gray-700">
                      <span className="font-semibold">Role:</span>{" "}
                      {project.role}
                    </p>
                    <div className="mt-2">
                      <span className="font-semibold text-gray-700">
                        Tech Stack:
                      </span>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {(project.tech_stack || []).map((tech, i) => (
                          <span
                            key={i}
                            className="bg-indigo-100 text-indigo-800 px-2 py-1 rounded-full text-sm"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
