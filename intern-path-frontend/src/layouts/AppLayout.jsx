import { Outlet } from "react-router-dom";
import Navbar from "../component/Navbar";
import React from "react";

const AppLayout = () => {
  return (
    <>
      <Navbar />
      <main className="pt-16 min-h-screen bg-[#f5f7fb] overflow-x-hidden">
        <div className="max-w-7xl mx-auto px-6 ">
          <Outlet />
        </div>
      </main>
    </>
  );
};

export default AppLayout;
