import {createContext,useState,useEffect} from "react"
import {jwtDecode} from "jwt-decode"
import React from "react";
import {useNavigate} from "react-router-dom"
export const UserContext = createContext();

export const UserProvider = ({children}) => {
    const navigate = useNavigate()
    const [user,setUser] = useState(null)
    const [loading,setLoading] = useState(true)

    useEffect(()=> {

        const token = localStorage.getItem("access_token");
        console.log(token)
        if(token) {
            try {
                const decoded = jwtDecode(token)
                console.log(decoded)
                setUser({
                    id:decoded.sub,
                    name:decoded.username
                })
            }
            catch(err) {
                console.log("Invalid token");
                setUser(null)
            }
            
        }
        setLoading(false)

    },[])

    const logout = () => {
        localStorage.removeItem("access_token");
        setUser(null)
        navigate("/login")
    }

    return (
        <UserContext.Provider value={{user,setUser,loading,logout}} >
            {children}

        </UserContext.Provider>
    )
}