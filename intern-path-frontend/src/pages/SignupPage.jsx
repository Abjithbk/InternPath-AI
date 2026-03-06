import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom';
import api from '../axios'
import { toast } from 'react-toastify'
import { useContext } from 'react';
import { UserContext } from '../context/UserContext';
import { jwtDecode } from 'jwt-decode';

// Floating Label Input Component
const FloatingInput = ({ label, name, type = "text", value, onChange, required, autoComplete }) => {
  const [focused, setFocused] = useState(false);
  const isFloated = focused || value.length > 0;

  return (
    <div className="relative border border-gray-300 rounded-lg px-3 pt-3 pb-2 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-all">
      <label
        className={`absolute left-3 transition-all duration-200 pointer-events-none text-gray-600  ${
          isFloated
            ? '-top-2.5 text-xs bg-white px-1 text-indigo-500'
            : 'top-3.5 text-sm'
        }`}
      >
        {label}
      </label>
      <input
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        autoComplete={autoComplete}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        className="w-full bg-transparent outline-none text-sm text-gray-800 pt-1"
      />
    </div>
  );
};

const SignupPage = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    second_name: '',
    email: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate();
  const { setUser, setUserProfile } = useContext(UserContext);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  }

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true)
    try {
      const res = await api.post("/signup", formData)
      const token = res.data.access_token;
      if (!token) {
        toast.error("Login failed");
        return;
      }
      localStorage.setItem("access_token", token)

      try {
        const decoded = jwtDecode(token)
        setUser({
          id: decoded.sub,
          name: decoded.username,
        })
      } catch {
        setUser(null)
      }

      // New users may not have a profile yet.
      setUserProfile(null)
      toast.success("Signup successfully..")
      navigate("/");
    }
    catch (error) {
      toast.error(error.response?.data?.message || "Something went wrong..")
    }
    finally {
      setLoading(false)
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white font-sans">
      <div className="w-full max-w-xl px-6">

        {/* Heading */}
        <h1 className="text-3xl font-bold text-center text-slate-900 mb-10">
          Welcome To InternPath
        </h1>

        {/* Form */}
        <form onSubmit={handleSignup} className="space-y-5">

          {/* Name Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FloatingInput
              label="First Name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              required
              autoComplete="off"
            />
            <FloatingInput
              label="Second Name"
              name="second_name"
              value={formData.second_name}
              onChange={handleChange}
              required
              autoComplete="off"
            />
          </div>

          {/* Email */}
          <FloatingInput
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            required
            autoComplete="off"
          />

          {/* Password */}
          <FloatingInput
            label="Password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            required
            autoComplete="off"
          />

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className={`w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition flex justify-center items-center ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-600 mt-6">
          If you already have an account?{" "}
          <span
            onClick={() => navigate("/Login")}
            className="text-indigo-600 font-medium cursor-pointer hover:underline"
          >
            Sign in
          </span>
        </p>
      </div>
    </div>
  )
}

export default SignupPage