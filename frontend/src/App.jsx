


// Created by: Stuart Smith
// Student ID: S2336002
// Date Created: 2025-04-17
// Description:
// Main layout for the PC Build Recommendation System with navigation links,
// user authentication (login/logout), and page routing.

import { Routes, Route, Link, useNavigate } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";

import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Recommender from "./pages/Recommender";
import About from "./pages/About";

import "./styles/App.css";

function App() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (storedToken) {
      try {
        const decoded = jwtDecode(storedToken);
        const now = Math.floor(Date.now() / 1000);
        if (decoded.exp && decoded.exp > now) {
          setUser({ username: decoded.sub });
          const timeoutDuration = (decoded.exp - now) * 1000;
          const timeoutId = setTimeout(() => {
            handleLogout();
            toast.info("Session expired. Please login again.");
          }, timeoutDuration);
          return () => clearTimeout(timeoutId);
        } else {
          localStorage.removeItem("access_token");
        }
      } catch {
        localStorage.removeItem("access_token");
      }
    }
  }, []);

  const handleLogin = (accessToken, username) => {
    localStorage.setItem("access_token", accessToken);
    setUser({ username });
    toast.success("✅ Welcome!");
    navigate("/");
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    toast.success("✅ Logged out successfully!");
    navigate("/login");
  };

  return (
    <>
      <nav className="nav-bar">
        <div className="nav-title">
          PC Build Recommender
        </div>

        <div className="nav-links">
          <Link to="/" className="nav-link">Home</Link>

          {!user ? (
            <>
              <Link to="/register" className="nav-link">Register</Link>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/about" className="nav-link">About</Link>
            </>
          ) : (
            <>
              <span className="nav-user">👋 Hello, {user.username}</span>
              <button onClick={handleLogout} className="btn-logout">
                Logout
              </button>
            </>
          )}
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home user={user} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/recommender" element={<Recommender />} />
        <Route path="/about" element={<About />} />
      </Routes>

      <ToastContainer position="bottom-right" />
    </>
  );
}

export default App;