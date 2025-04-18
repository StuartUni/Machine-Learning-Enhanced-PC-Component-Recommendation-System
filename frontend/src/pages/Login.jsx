// Created by: Stuart Smith
// Student ID: S2336002
// Date Created: 2025-04-17
// Description:
// Page containing the login form for the PC Build Recommendation System.

import { Link } from "react-router-dom";
import LoginForm from "../components/LoginForm";
import "../styles/Login.css";

function Login({ onLogin }) {
  return (
    <div className="login-container">
      <h2 className="login-title">🔐 Login to Your Account</h2>
      <LoginForm onLogin={onLogin} />
      <div style={{ marginTop: "1rem" }}>
        <Link to="/">🏠 Back to Home</Link>
      </div>
    </div>
  );
}

export default Login;