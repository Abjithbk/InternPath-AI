import React from "react"
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
      </Router>
    </div>
  )
}

export default App
