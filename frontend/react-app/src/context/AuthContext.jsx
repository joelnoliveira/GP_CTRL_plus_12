import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [isLoggedIn,setLoggedIn] = useState(false);

    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        setToken(storedToken);
        setLoggedIn(!!storedToken);
    }, []);

    

    const login = (newToken) => {
        localStorage.setItem('token', newToken);
        setToken(newToken);
        setLoggedIn(true);
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setLoggedIn(false);
    };

    return (
        <AuthContext.Provider value={{ isLoggedIn, token, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);