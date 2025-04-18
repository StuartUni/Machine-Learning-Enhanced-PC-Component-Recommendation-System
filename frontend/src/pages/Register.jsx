// Created by: Stuart Smith
// Student ID: S2336002
// Date Created: 2025-04-17
// Description:
// Page containing the user registration form for the PC Build Recommendation System.

import RegisterForm from "../components/RegisterForm"; 
import { Link } from "react-router-dom";
import "../styles/Register.css"; 

function Register() { 
  return (
    <div className="register-container">
      <h2 className="register-title">📝 Create an Account</h2>
      <RegisterForm />
      <div style={{ marginTop: "1rem", textAlign: "center" }}>
        <Link to="/">🏠 Back to Home</Link>
      </div>
    </div>
  );
}

export default Register;