import React, { useState } from "react";
import { FcGoogle } from "react-icons/fc";
import { useNavigate } from "react-router-dom";
import api from "../axios";
import { toast } from "react-toastify";
import { GoogleLogin } from "@react-oauth/google";
import { useContext } from "react";
import { UserContext } from "../context/UserContext";
import { jwtDecode } from "jwt-decode";


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

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState({});
  const { setUser, setUserProfile } = useContext(UserContext);
  const [loading,setLoading] = useState(false)

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    if (errors[name] || errors.auth) {
      setErrors((prev) => ({ ...prev, [name]: undefined, auth: undefined }));
    }
  };

 const handleLogin = async (e) => {
  e.preventDefault();
  const nextErrors = {};
  if (!formData.email.trim()) {
    nextErrors.email = "Email is required";
  }
  if (!formData.password) {
    nextErrors.password = "Password is required";
  }

  if (Object.keys(nextErrors).length > 0) {
    setErrors(nextErrors);
    return;
  }

  setErrors({});
  setLoading(true)

  try {
    const res = await api.post("/login", formData);
    const token = res.data?.access_token;

    if (!token) {
      toast.error("Login failed");
      return;
    }

    localStorage.setItem("access_token", token);

    try {
      const decoded = jwtDecode(token);
      setUser({
        id: decoded.sub,
        name: decoded.username,
      });
    } catch {
      setUser(null);
    }

    try {
      const profileRes = await api.get("/profile/");
      setUserProfile(profileRes.data);
    } catch (profileErr) {
      if (profileErr.response?.status === 404) {
        setUserProfile(null);
      } else {
        throw profileErr;
      }
    }

    toast.success("Login successful 🎉");

    navigate("/");

  } catch (error) {
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

    if (typeof detail === "string") {
      const lowerDetail = detail.toLowerCase();

      // Login page should never show signup password policy errors.
      const isPasswordPolicyMessage =
        lowerDetail.includes("at least") ||
        lowerDetail.includes("uppercase") ||
        lowerDetail.includes("lowercase") ||
        lowerDetail.includes("special character");

      if (isPasswordPolicyMessage) {
        setErrors((prev) => ({ ...prev, password: "Invalid email or password" }));
        return;
      }

      if (lowerDetail.includes("email") || lowerDetail.includes("password") || lowerDetail.includes("credentials")) {
        setErrors((prev) => ({ ...prev, password: detail }));
        return;
      }
      setErrors((prev) => ({ ...prev, auth: detail }));
      return;
    }

    const fallbackMessage = error.response?.data?.message || "Invalid email or password";
    setErrors((prev) => ({ ...prev, auth: fallbackMessage }));
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

    try {
      const decoded = jwtDecode(accessToken);
      setUser({
        id: decoded.sub,
        name: decoded.username,
      });
    } catch {
      setUser(null);
    }

    try {
      const profileRes = await api.get("/profile/");
      setUserProfile(profileRes.data);
    } catch (profileErr) {
      if (profileErr.response?.status === 404) {
        setUserProfile(null);
      } else {
        throw profileErr;
      }
    }

    toast.success("Google Login Success 🎉");

    navigate("/");

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
        <form onSubmit={handleLogin} className="space-y-5">
          {errors.auth && (
            <p className="text-sm text-red-600">{errors.auth}</p>
          )}

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
            className={`w-full py-3 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
              loading
                ? "bg-indigo-400 cursor-not-allowed text-white"
                : "bg-indigo-600 hover:bg-indigo-700 text-white"
            }`}
          >
            {loading && (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            )}
            {loading ? "Logging in..." : "Login"}
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