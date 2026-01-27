import React, { useState } from 'react'
import { FcGoogle } from "react-icons/fc";
import { useNavigate } from 'react-router-dom';
import api from '../axios'
import {toast} from 'react-toastify'
const SignupPage = () => {
  const [formData,setFormData] = useState({
    first_name:'',
    second_name:'',
    email:'',
    password:''
  })
    const navigate = useNavigate();

    const handleChange = (e) => {
       setFormData({...formData,[e.target.name]:e.target.value});
    }
    const handleSignup = async (e) => {
       e.preventDefault();
       try {
         await api.post("/signup",formData)
         
         toast.success("Signup successfully..")
        navigate("/login");
       }
       catch(error) {
         toast.error(error.response?.data?.message || "Something went wrong..")
       }
    };
    
  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-xl px-6">
        {/* Heading */}
        <h1 className="text-3xl font-bold text-center text-slate-900 mb-10">
          Welcome To InternPath
        </h1>

        

        {/* Form */}
        <form onSubmit={handleSignup} className="space-y-6">
          {/* Name Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-600">First Name</label>
              <input
              name='first_name'
              value={formData.first_name}
              onChange={handleChange}
                type="text"
                className="w-full mt-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="text-sm text-gray-600">Second Name</label>
              <input
              name='second_name'
              value={formData.second_name}
              onChange={handleChange}
                type="text"
                className="w-full mt-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="text-sm text-gray-600">Email</label>
            <input
            name='email'
            value={formData.email}
            onChange={handleChange}
              type="email"
              className="w-full mt-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Password */}
          <div>
            <label className="text-sm text-gray-600">Password</label>
            <input
            name='password'
            value={formData.password}
            onChange={handleChange}
              type="password"
              className="w-full mt-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition"
          >
            Create Account
          </button>
        </form>
        <p className="text-center text-sm text-gray-600 mt-6">
          Don’t have an account?{" "}
          <span
            onClick={() => navigate("/Login")}
            className="text-indigo-600 font-medium cursor-pointer hover:underline"
          >
            Sign up
          </span>
        </p>
      </div>
    </div>
  )
}

export default SignupPage
