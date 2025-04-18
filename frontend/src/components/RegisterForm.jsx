// Created by: Stuart Smith
// Student ID: S2336002
// Date Created: 2025-04-15
// Description: Handles user registration via FastAPI backend (with Toastify notifications and redirect to login).

import { useState } from "react";
import { useNavigate } from "react-router-dom";  // ✅ Import navigate
import { registerUser } from "../api";
import { toast } from "react-toastify"; 

export default function RegisterForm() {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const navigate = useNavigate();  // ✅ Setup navigate()

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await registerUser(form);
      console.log("✅ Register API response:", data);

      toast.success(`✅ Registered as ${data.username}`);

      // ✅ Wait 1.2 seconds, then redirect to login page
      setTimeout(() => {
        navigate("/login");
      }, 1200);

    } catch (error) {
      console.error("Registration error:", error);
      toast.error("❌ Registration failed");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="register-form">
      <label>Username</label>
      <input
        name="username"
        placeholder="Username"
        onChange={handleChange}
        required
      />

      <label>Email</label>
      <input
        name="email"
        type="email"
        placeholder="Email"
        onChange={handleChange}
        required
      />

      <label>Password</label>
      <input
        name="password"
        type="password"
        placeholder="Password"
        onChange={handleChange}
        required
      />

      <button type="submit" className="btn-register-submit">
        Register
      </button>
    </form>
  );
}