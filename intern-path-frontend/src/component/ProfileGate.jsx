import { useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { UserContext } from "../context/UserContext";
import React from "react";
const ProfileGate = ({ children }) => {
  const { user,userProfile, loading } = useContext(UserContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading) {
      // If NOT logged in → go login
      if (!user) {
        navigate("/login");
        return;
      }

      // If logged in but no profile → go profile completion
      if (user && !userProfile) {
        navigate("/profile-completion");
      }
    }
  }, [loading, userProfile, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="h-10 w-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return children;
};

export default ProfileGate;