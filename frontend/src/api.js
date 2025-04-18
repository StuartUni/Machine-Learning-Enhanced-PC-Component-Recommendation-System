// Created by: Stuart Smith
// Student ID: S2336002
// Date Created: 2025-04-10
// Description:
// Defines helper functions to interact with FastAPI backend:
// - Hybrid build recommendation
// - User registration and login (JWT)
// - Save, retrieve, rate, and delete multiple user builds (JWT-protected)

const API_BASE_URL = "http://localhost:8000";

/**
 * Sends a POST request to the backend with the given user inputs.
 * @param {Object} input - The user input (budget, query, user_id, mode).
 * @returns {Promise<Object>} The recommended build data from backend.
 */
export async function getTestRecommendation(input) {
  const response = await fetch(`${API_BASE_URL}/api/recommend`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch recommendation");
  }

  return await response.json();
}

/**
 * Sends a registration request to the backend.
 * @param {Object} userData - { username, email, password }
 * @returns {Promise<Object>} Registered user details
 */
export async function registerUser(userData) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    throw new Error("Registration failed");
  }

  return await response.json();
}

/**
 * Sends login credentials to backend and returns JWT token.
 * @param {Object} formData - { username, password }
 * @returns {Promise<Object>} { access_token, token_type }
 */
export async function loginUser(formData) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });

  const data = await response.json();
  console.log("🚀 Login API response:", data);

  if (!response.ok) {
    throw new Error("Login failed");
  }

  return data;
}

/**
 * Saves a build to the user's account (supports multiple builds) (requires JWT).
 * @param {Object} build - The recommended build object.
 * @param {string} token - The JWT token.
 * @returns {Promise<Object>} Backend confirmation message.
 */
export async function saveBuild(build, token) {
  const response = await fetch(`${API_BASE_URL}/auth/save_build`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(build),
  });

  if (!response.ok) {
    throw new Error("Failed to save build");
  }

  return await response.json();
}

/**
 * Fetches all saved builds for the authenticated user (requires JWT).
 * @param {string} token - The JWT token.
 * @returns {Promise<Object>} Saved builds array
 */
export async function getSavedBuilds(token) {
  const response = await fetch(`${API_BASE_URL}/auth/my_builds`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch saved builds");
  }

  return await response.json();
}

/**
 * Rates a build (requires JWT).
 * @param {Object} ratingData - { build_id, rating }
 * @param {string} token - The JWT token.
 * @returns {Promise<Object>} Backend confirmation message.
 */
export async function rateBuild(ratingData, token) {
  const response = await fetch(`${API_BASE_URL}/auth/rate-build`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(ratingData),
  });

  if (!response.ok) {
    throw new Error("Rating failed");
  }

  return await response.json();
}

/**
 * Deletes a saved build by build_id (requires JWT).
 * @param {string} build_id - The ID of the build to delete.
 * @param {string} token - The JWT token.
 * @returns {Promise<Object>} Backend confirmation message.
 */
export async function deleteSavedBuild(build_id, token) {
  const response = await fetch(`${API_BASE_URL}/auth/delete_build/${build_id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to delete build");
  }

  return await response.json();
}