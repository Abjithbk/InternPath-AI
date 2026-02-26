import { useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { UserContext } from "../context/UserContext";
import React from "react";
const ProfileGate = ({ children }) => {
  const { user,userProfile, loading } = useContext(UserContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (loading) return;

    // Not logged in
    if (!user) {
      if (location.pathname !== "/login") {
        navigate("/login");
      }
      return;
    }

    // Logged in but NO profile
    if (user && userProfile === null) {
      if (location.pathname !== "/profile-completion") {
        navigate("/profile-completion");
      }
      return;
    }
  }, [loading, userProfile, navigate,user]);

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