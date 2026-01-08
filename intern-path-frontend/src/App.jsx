import React from "react"
import {BrowserRouter as Router,Routes,Route} from 'react-router-dom'
import LoginPage from "./component/LoginPage"
import Dashboard from "./component/Dashboard"
function App() {
  return (
    <div>
      <Router basename="">
          <Routes>
            <Route path="/" element={<Dashboard/>} />
            <Route path="/Login" element={<LoginPage/>} />
          </Routes>
      </Router>
    </div>
  )
}

export default App
