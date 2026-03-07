import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom';
import api from '../axios'
import { toast } from 'react-toastify'
import { useContext } from 'react';
import { UserContext } from '../context/UserContext';
import { jwtDecode } from 'jwt-decode';

// Floating Label Input Component
const FloatingInput = ({ label, name, type = "text", value, onChange, required, autoComplete, error }) => {
  const [focused, setFocused] = useState(false);
  const isFloated = focused || value.length > 0;

  return (
    <div>
      <div
        className={`relative border rounded-lg px-3 pt-3 pb-2 transition-all ${
          error
            ? 'border-red-500 focus-within:border-red-500 focus-within:ring-1 focus-within:ring-red-500'
            : 'border-gray-300 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500'
        }`}
      >
        <label
          className={`absolute left-3 transition-all duration-200 pointer-events-none text-gray-600 ${
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
          aria-invalid={Boolean(error)}
          className="w-full bg-transparent outline-none text-sm text-gray-800 pt-1"
        />
      </div>
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
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
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate();
  const { setUser, setUserProfile } = useContext(UserContext);

  const validatePassword = (password) => {
    if (password.length < 8) return 'Password must be at least 8 characters long';
    if (!/[A-Z]/.test(password)) return 'Password must contain at least one uppercase letter';
    if (!/[a-z]/.test(password)) return 'Password must contain at least one lowercase letter';
    if (!/\d/.test(password)) return 'Password must contain at least one number';
    if (!/[^A-Za-z0-9]/.test(password)) return 'Password must contain at least one special character';
    return '';
  };

  const validateForm = () => {
    const nextErrors = {};
    if (!formData.password) {
      nextErrors.password = 'Password is required';
      return nextErrors;
    }

    const passwordError = validatePassword(formData.password);
    if (passwordError) nextErrors.password = passwordError;
    return nextErrors;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    if (name === 'password') {
      if (!value) {
        setErrors((prev) => ({ ...prev, password: undefined }));
        return;
      }

      const passwordError = validatePassword(value);
      setErrors((prev) => ({ ...prev, password: passwordError || undefined }));
      return;
    }

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  }

  const handleSignup = async (e) => {
    e.preventDefault();
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

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

      // Hydrate profile state so route guards can decide correctly.
      try {
        const profileRes = await api.get("/profile/")
        setUserProfile(profileRes.data)
      } catch (profileErr) {
        if (profileErr.response?.status === 404) {
          setUserProfile(null)
        } else {
          throw profileErr
        }
      }

      toast.success("Signup successfully..")
      navigate("/");
    }
    catch (error) {
      const detail = error.response?.data?.detail;

      if (Array.isArray(detail)) {
        const apiErrors = {};
        detail.forEach((item) => {
          const field = item?.loc?.[item.loc.length - 1];
          if (field) apiErrors[field] = item.msg;
        });
        if (Object.keys(apiErrors).length > 0) {
          setErrors(apiErrors);
          return;
        }
      }

      if (typeof detail === 'string' && detail.toLowerCase().includes('password')) {
        setErrors((prev) => ({ ...prev, password: detail }));
        return;
      }

      toast.error(error.response?.data?.message || detail || "Something went wrong..")
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
              error={errors.first_name}
            />
            <FloatingInput
              label="Second Name"
              name="second_name"
              value={formData.second_name}
              onChange={handleChange}
              required
              autoComplete="off"
              error={errors.second_name}
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
            error={errors.email}
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
            error={errors.password}
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