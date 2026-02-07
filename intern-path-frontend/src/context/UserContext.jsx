import {createContext,useState,useEffect} from "react"
import {jwtDecode} from "jwt-decode"
import React from "react";
export const UserContext = createContext();

export const UserProvider = ({children}) => {
    const [user,setUser] = useState(null)

    useEffect(()=> {

        const token = localStorage.getItem("access_token");
        console.log(token)
        if(token) {
            const decoded = jwtDecode(token)
            console.log(decoded)
            setUser({
                id:decoded.sub,
                name:decoded.username
            })
            console.log(user)
        }

    },[])

    return (
        <UserContext.Provider value={{user,setUser}} >
            {children}

        </UserContext.Provider>
    )
}