import React, { useEffect, useState } from "react";
import api from "../axios"
import {useNavigate} from "react-router-dom"
import { toast } from "react-toastify";
const CompleteProfile = () => {
    const navigate = useNavigate()
  const [formData, setFormData] = useState({
    year: "",
    semester: "",
    college: "",
    course: "",
    cgpa: "",
    skills: [],
    projects: [{ title: "", description: "" }],
  });

  const [skillInput, setSkillInput] = useState("");

  useEffect(() => {
    const checkProfile = async () => {
      try {
        const res = await api.get("/profile/");
        const profile = res.data;
        console.log(profile)

        // If profile exists, redirect to HeroSection
        if (profile && Object.keys(profile).length > 0) {
          navigate("/"); // change "/hero" to your HeroSection route
        }
      } catch (err) {
        console.log("No profile found, stay on this page");
        // If API returns 404, do nothing — user fills profile
      }
    };

    checkProfile();
  },[navigate])
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const addSkill = (e) => {
    if (e.key === "Enter" && skillInput.trim()) {
      e.preventDefault();
      setFormData({
        ...formData,
        skills: [...formData.skills, skillInput.trim()],
      });
      setSkillInput("");
    }
  };

  const removeSkill = (skill) => {
    setFormData({
      ...formData,
      skills: formData.skills.filter((s) => s !== skill),
    });
  };

  const handleProjectChange = (index, field, value) => {
    const updated = [...formData.projects];
    updated[index][field] = value;
    setFormData({ ...formData, projects: updated });
  };

  const addProject = () => {
    setFormData({
      ...formData,
      projects: [...formData.projects, { title: "", description: "" }],
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
        await api.post("/profile/",{
            year:Number(formData.year),
            semester:Number(formData.semester),
            college:formData.college,
            course:formData.course,
            cgpa:Number(formData.cgpa),
            skills:formData.skills,
            projects:formData.projects
        });

        navigate("/dashboard")
    }
    catch(err) {
        if(err.response?.status == 400) {
            toast.error("Profile already exists");
        }
        else {
            toast.error("Something went wrong")
        }
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F7FB] flex items-center justify-center px-6 py-10">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-4xl bg-white rounded-2xl border border-gray-200 p-8"
      >
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-2xl font-semibold text-gray-900">
            Complete Your Profile
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            This helps us personalize internships for you
          </p>
        </div>

        {/* Academic Info */}
        <section className="mb-10">
          <h2 className="text-lg font-medium text-gray-900 mb-5">
            Academic Details
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <input
              type="number"
              name="year"
              value={formData.year}
              onChange={handleChange}
              placeholder="Year"
              className="input"
            />

            <input
              type="number"
              name="semester"
              value={formData.semester}
              onChange={handleChange}
              placeholder="Semester"
              className="input"
            />

            <input
              type="text"
              name="college"
              value={formData.college}
              onChange={handleChange}
              placeholder="College"
              className="input"
            />

            <input
              type="text"
              name="course"
              value={formData.course}
              onChange={handleChange}
              placeholder="Course"
              className="input"
            />

            <input
              type="number"
              step="0.01"
              name="cgpa"
              value={formData.cgpa}
              onChange={handleChange}
              placeholder="CGPA"
              className="input"
            />
          </div>
        </section>

        {/* Skills */}
        <section className="mb-10">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Skills
          </h2>

          <input
            type="text"
            value={skillInput}
            onChange={(e) => setSkillInput(e.target.value)}
            onKeyDown={addSkill}
            placeholder="Type a skill and press Enter"
            className="input"
          />

          <div className="flex flex-wrap gap-2 mt-4">
            {formData.skills.map((skill, i) => (
              <span
                key={i}
                onClick={() => removeSkill(skill)}
                className="
                  px-3 py-1 text-sm font-medium
                  bg-indigo-50 text-indigo-600
                  rounded-full cursor-pointer
                  hover:bg-indigo-100
                "
              >
                {skill} ✕
              </span>
            ))}
          </div>
        </section>

        {/* Projects */}
        <section className="mb-10">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Projects
          </h2>

          {formData.projects.map((project, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-xl p-5 mb-4"
            >
              <input
                type="text"
                placeholder="Project Title"
                value={project.title}
                onChange={(e) =>
                  handleProjectChange(index, "title", e.target.value)
                }
                className="input mb-3"
              />

              <textarea
                rows="3"
                placeholder="Project Description"
                value={project.description}
                onChange={(e) =>
                  handleProjectChange(index, "description", e.target.value)
                }
                className="input resize-none"
              />
            </div>
          ))}

          <button
            type="button"
            onClick={addProject}
            className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
          >
            + Add another project
          </button>
        </section>

        {/* Submit */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="
              bg-indigo-600 text-white
              px-6 py-3 rounded-xl
              font-medium text-sm
              hover:bg-indigo-700 transition
            "
          >
            Save & Continue
          </button>
        </div>
      </form>
    </div>
  );
};

export default CompleteProfile;
