import { createContext, useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";
import api from "../axios";
import React from "react";

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const decoded = jwtDecode(token);

        // ✅ Check expiry
        if (decoded.exp * 1000 < Date.now()) {
          localStorage.removeItem("access_token");
          setLoading(false);
          return;
        }

        setUser({
          id: decoded.sub,
          name: decoded.username,
        });

        // ✅ Fetch profile ONLY ONCE
        const res = await api.get("/profile/");
        setUserProfile(res.data);

      } catch (err) {
        console.log("Auth error:", err);
        localStorage.removeItem("access_token");
        setUser(null);
        setUserProfile(null);
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    setUserProfile(null);
    navigate("/login");
  };

  return (
    <UserContext.Provider
      value={{
        user,
        setUser,
        userProfile,
        setUserProfile,
        loading,
        logout,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};