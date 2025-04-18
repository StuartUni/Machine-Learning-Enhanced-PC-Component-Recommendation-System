// Created by: Stuart Smith
// Student ID: S2336002
// Date Created: 2025-04-17
// Description:
// Home page for the PC Build Recommendation System. Shows dynamic links based on login state.

import { Link } from "react-router-dom";
import "../styles/Home.css"; 

function Home({ user }) {
  return (
    <div className="home-container">
      <h1 className="home-title">🚀 Welcome to the PC Build Recommendation System</h1>

      <div className="home-buttons">
        {user ? (
          <>
            <span className="home-welcome">👋 Hello, {user.username}!</span>
            <Link to="/recommender" className="btn-home">🔧 Recommender</Link>
          </>
        ) : (
          <>
            <Link to="/register" className="btn-home">📝 Register</Link>
            <Link to="/login" className="btn-home">🔐 Login</Link>
            <Link to="/recommender" className="btn-home">🔧 Recommender</Link>
          </>
        )}
      </div>
    </div>
  );
}

export default Home;