// Created by: Stuart Smith
// Student ID: S2336002
// Date Created: 2025-04-17
// Description:
// Login form component for PC Build Recommendation System (with Toastify notifications and redirect to Home).

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api";
import { toast } from "react-toastify";
import "../styles/Login.css";

export default function LoginForm({ onLogin }) {
  const [form, setForm] = useState({ username: "", password: "" });
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await loginUser(form);
      console.log("✅ Login API response:", data);

      if (onLogin) {
        onLogin(data.access_token, form.username);  
      }

      toast.success("✅ Welcome back!");

      setMessage("");

      setTimeout(() => {
        navigate("/");
      }, 1200);
    } catch (error) {
      console.error("Login error:", error);
      setMessage("❌ Login failed");
      toast.error("❌ Login failed");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <label>Username:</label>
      <input
        name="username"
        value={form.username}
        onChange={handleChange}
        required
      />

      <label>Password:</label>
      <input
        name="password"
        type="password"
        value={form.password}
        onChange={handleChange}
        required
      />

      <button type="submit" className="btn-login-submit">
        Login
      </button>

      {message && <p className="login-message">{message}</p>}
    </form>
  );
}