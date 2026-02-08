import React from "react"
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import {BrowserRouter as Router,Routes,Route} from 'react-router-dom'
import HeroSection from "./pages/HeroSection"
import Internship from "./pages/internship"
import InternshipDetails from "./pages/InternshipDetails"
import Chatbot from "./pages/Chatbot"
import SignupPage from "./pages/SignupPage"
import LoginPage from "./pages/LoginPage"
import AppLayout from "./layouts/AppLayout";
import Dashboard from "./pages/Dashboard";
import ResumeAssessment from "./pages/ResumeAssessment";
import FakeInternship from "./pages/FakeInternship";
import CompleteProfile from "./pages/CompleteProfile";
import { UserProvider } from "./context/UserContext.jsx";
function App() {
  return (
    <div>
      <Router basename="">
      <UserProvider>
          <Routes>
            <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/Internship" element={<Internship/>} />
            <Route path="/resume" element={<ResumeAssessment />} />
            <Route path="fake-internship" element={<FakeInternship/>} />
            </Route>
            <Route path="/Internship/:id" element={<InternshipDetails/>} />
            <Route path="/" element={<HeroSection/>} />
            <Route path="/Signup" element={<SignupPage/>} />
            <Route path="/Login" element={<LoginPage />} />
            <Route path="/Chatbot" element={<Chatbot/>} />
            <Route path="profile-completion" element={<CompleteProfile />} />
          </Routes>
            <ToastContainer
              position="top-right"
              autoClose={3000}
              hideProgressBar={false}
              closeOnClick
              pauseOnHover
              draggable
            />
      </UserProvider>
      </Router>
    </div>
  )
}

export default App
