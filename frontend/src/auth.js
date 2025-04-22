// Created by: Stuart Smith
// Student ID: S2336002
// Date Created: 2025-04-15
// Description:
// Handles registration and login requests to the FastAPI backend.

const API_BASE_URL = "http://localhost:8000";

export async function registerUser(username, password) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return await response.json();
}

export async function loginUser(username, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }

  return await response.json(); 
}