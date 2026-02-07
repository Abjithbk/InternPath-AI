import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import React from "react";

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

  const isChatbotPage = location.pathname === "/chatbot";

  return (
    <nav className="fixed top-0 left-0 w-full h-16 bg-[#f5f7ff] border-b border-gray-100 z-50">
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">

        {/* LEFT SIDE */}
        <div className="flex items-center gap-3">
          {isChatbotPage ? (
            <>
              <button
                onClick={() => navigate(-1)}
                className="p-2 rounded-lg hover:bg-gray-200"
              >
                <ArrowLeft className="w-5 h-5 text-indigo-600" />
              </button>
              <h1 className="text-lg font-semibold text-indigo-600">
                Chatbot
              </h1>
            </>
          ) : (
            <h1 className="text-xl font-bold text-indigo-600">
              InternPath
            </h1>
          )}
        </div>

        {/* RIGHT SIDE */}
        {!isChatbotPage && (
          <div className="flex gap-8">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.path}
                className={({ isActive }) =>
                  `relative text-sm font-medium transition ${
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
      </div>
    </nav>
  );
};

export default Navbar;
