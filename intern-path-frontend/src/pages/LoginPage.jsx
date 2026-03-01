import React, { useState } from "react";
import { FcGoogle } from "react-icons/fc";
import { useNavigate } from "react-router-dom";
import api from "../axios";
import { toast } from "react-toastify";
import { GoogleLogin } from "@react-oauth/google";
import { useContext } from "react";
import { UserContext } from "../context/UserContext";

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const { setUser, setUserProfile } = useContext(UserContext);
  const [loading,setLoading] = useState(false)

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

 const handleLogin = async (e) => {
  e.preventDefault();
  setLoading(true)

  try {
    const res = await api.post("/Login", formData);
    const token = res.data?.access_token;

    if (!token) {
      toast.error("Login failed");
      return;
    }

    localStorage.setItem("access_token", token);

    toast.success("Login successful 🎉");

    // Just reload app state
    window.location.href = "/";

  } catch (error) {
    toast.error(
      error.response?.data?.message ||
      error.response?.data?.detail ||
      "Invalid email or password"
    );
  }
  finally {
    setLoading(false)
  }
};

 const handleGoogleLogin = async (response) => {
  try {
    const googleToken = response.credential;

    const res = await api.post("/google-auth", { token: googleToken });
    const accessToken = res.data?.access_token;

    if (!accessToken) {
      toast.error("Google login failed");
      return;
    }

    localStorage.setItem("access_token", accessToken);

    toast.success("Google Login Success 🎉");

    window.location.href = "/";

  } catch (err) {
    toast.error("Google login failed!");
  }
};

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-xl px-6">
        {/* Heading */}
        <h1 className="text-3xl font-bold text-center text-slate-900 mb-10">
          Welcome Back to InternPath
        </h1>

        
          <GoogleLogin
            onSuccess={handleGoogleLogin}
            onError={() => toast.error("Google Login Failed")}
            render={(renderProps) => (
              <button
                onClick={renderProps.onClick}
                disabled={renderProps.disabled}
                className="w-full flex items-center justify-center gap-3 border border-gray-300 rounded-full py-3 text-sm font-medium hover:bg-gray-50 transition"
              >
                <FcGoogle size={20} />
                Continue with Google
              </button>
            )}
          />
        

        {/* OR Divider */}
        <div className="flex items-center my-8">
          <div className="flex-1 h-px bg-gray-300"></div>
          <span className="px-4 text-gray-500 text-sm">OR</span>
          <div className="flex-1 h-px bg-gray-300"></div>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-6">
          {/* Email */}
          <div>
            <label className="text-sm text-gray-600">Email</label>
            <input
              name="email"
              value={formData.email}
              onChange={handleChange}
              type="email"
              required
              className="w-full mt-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Password */}
          <div>
            <label className="text-sm text-gray-600">Password</label>
            <input
              name="password"
              value={formData.password}
              onChange={handleChange}
              type="password"
              required
              className="w-full mt-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 rounded-lg font-semibold transition flex items-center justify-center gap-2
            ${loading 
              ? "bg-indigo-400 cursor-not-allowed text-white" 
              : "bg-indigo-600 hover:bg-indigo-700 text-white"
            }`}
          >
            {
              loading && (
    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>)
            }
            {loading ? "Logging in...": "Login"}
          </button>
        </form>

        {/* Footer */}
        <p className="text-center text-sm text-gray-600 mt-6">
          Don't have an account?{" "}
          <span
            onClick={() => navigate("/Signup")}
            className="text-indigo-600 font-medium cursor-pointer hover:underline"
          >
            Sign up
          </span>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;