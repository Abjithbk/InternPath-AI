import React from "react"
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import {BrowserRouter as Router,Routes,Route} from 'react-router-dom'
import Dashboard from "./pages/Dashboard"
import Internship from "./pages/internship"
import InternshipDetails from "./pages/InternshipDetails"
import Chatbot from "./pages/Chatbot"
import SignupPage from "./pages/SignupPage"
import LoginPage from "./pages/LoginPage"
function App() {
  return (
    <div>
      <Router basename="">
          <Routes>
            <Route path="/" element={<Dashboard/>} />
            <Route path="/Signup" element={<SignupPage/>} />
            <Route path="/Login" element={<LoginPage />} />
            <Route path="/Internship" element={<Internship/>} />
            <Route path="/Internship/:id" element={<InternshipDetails/>} />
            <Route path="/Chatbot" element={<Chatbot/>} />
          </Routes>
            <ToastContainer
              position="top-right"
              autoClose={3000}
              hideProgressBar={false}
              closeOnClick
              pauseOnHover
              draggable
            />
      </Router>
    </div>
  )
}

export default App
