import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, LogOut } from "lucide-react";
import React, { useContext } from "react";
import { UserContext } from "../context/UserContext";

const navItems = [
  { name: "Dashboard", path: "/dashboard" },
  { name: "Internships", path: "/internship" },
  { name: "Resume", path: "/resume" },
  { name: "Fake Internship", path: "/fake-internship" },
  { name: "Chatbot", path: "/chatbot" },
];

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useContext(UserContext);

  const isChatbotPage = location.pathname === "/chatbot";

  return (
    <nav className="fixed top-0 left-0 w-full h-16 bg-[#f5f7ff] shadow-sm z-50">
      <div className="w-full px-8 h-full flex items-center justify-between">

        {/* LEFT */}
        <div className="flex items-center gap-3">
          {isChatbotPage ? (
            <>
              <button
                onClick={() => navigate(-1)}
                className="p-2 rounded-lg hover:bg-gray-200"
              >
                <ArrowLeft className="w-5 h-5 text-indigo-600" />
              </button>
              <span className="text-lg font-semibold text-indigo-600">
                Chatbot
              </span>
            </>
          ) : (
            <span className="text-xl font-bold text-indigo-600">
              InternPath
            </span>
          )}
        </div>

        {/* CENTER NAV */}
        {!isChatbotPage && (
          <div className="flex justify-center gap-8">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.path}
                className={({ isActive }) =>
                  `relative text-sm font-medium transition whitespace-nowrap ${
                    isActive
                      ? "text-indigo-600"
                      : "text-gray-600 hover:text-indigo-600"
                  }`
                }
              >
                {item.name}
              </NavLink>
            ))}
          </div>
        )}

        {/* RIGHT LOGOUT */}
        <div className="flex justify-end">
          {!isChatbotPage && (
            <button
              onClick={logout}
              className="p-2 rounded-lg hover:bg-red-100 text-red-600"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          )}
        </div>

      </div>
    </nav>
  );
};

export default Navbar;
