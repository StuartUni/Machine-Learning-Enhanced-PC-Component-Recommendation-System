// Created by: Stuart Smith
// Student ID: S2336002
// Date Created: 2025-04-17
// Description:
// Page for PC Build Recommender with input form, recommendation, save, view saved builds, delete build, and rating.

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import { getTestRecommendation, saveBuild, getSavedBuilds, rateBuild, deleteSavedBuild } from "../api";
import StarRating from "../components/StarRating";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "../styles/Recommender.css";

function Recommender() {
  const [budget, setBudget] = useState("");
  const [useCase, setUseCase] = useState("general");
  const [game, setGame] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [token, setToken] = useState(null);
  const [savedBuilds, setSavedBuilds] = useState([]);
  const [selectedRating, setSelectedRating] = useState(0);

  const navigate = useNavigate();

  useEffect(() => {
    const stored = localStorage.getItem("access_token");
    if (stored) {
      try {
        const decoded = jwtDecode(stored);
        const now = Math.floor(Date.now() / 1000);
        if (decoded.exp && decoded.exp > now) {
          setToken(stored);
        } else {
          localStorage.removeItem("access_token");
          toast.info("Session expired. Please login again.");
          navigate("/login");
        }
      } catch {
        localStorage.removeItem("access_token");
        navigate("/login");
      }
    } else {
      navigate("/login");
    }
  }, [navigate]);

  
  useEffect(() => {
    if (token) {
      handleViewSaved();
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);

    const query = useCase === "gaming" ? game : useCase;

    try {
      let username = "guest";
      if (token) {
        const decoded = jwtDecode(token);
        if (decoded?.sub) {
          username = decoded.sub;
        }
      }

      const recommendation = await getTestRecommendation({
        budget: parseInt(budget),
        query,
        user_id: username,
        mode: "hybrid",
      });

      setResult(recommendation);
    } catch (err) {
      console.error(err);
      setError("Failed to get recommendation.");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveBuild = async () => {
    if (!token || !result?.recommended_build) {
      toast.error("You must be logged in to save a build.");
      return;
    }

    const alreadySaved = savedBuilds.some(
      (build) => build.build_id === result.recommended_build.build_id
    );

    if (alreadySaved) {
      toast.info("⚠️ Build already saved.");
      return;
    }

    try {
      const buildToSave = {
        ...result.recommended_build,
        total_cost: result.total_cost,
      };
      const response = await saveBuild(buildToSave, token);
      toast.success(response.message || "✅ Build saved!");
      await handleViewSaved();
    } catch {
      toast.error("❌ Failed to save build.");
    }
  };

  const handleViewSaved = async () => {
    if (!token) {
      toast.error("You must be logged in to view saved builds.");
      return;
    }
    try {
      const response = await getSavedBuilds(token);
      setSavedBuilds(response.saved_builds || []);
    } catch {
      toast.error("❌ Failed to fetch saved builds.");
    }
  };

  const handleSubmitRating = async () => {
    if (!token || !result?.recommended_build?.build_id || selectedRating === 0) {
      toast.error("Please select a rating and ensure you're logged in.");
      return;
    }
    try {
      const response = await rateBuild({
        build_id: result.recommended_build.build_id,
        rating: selectedRating,
      }, token);
      toast.success(response.message || "✅ Rating submitted!");
      setSelectedRating(0);
    } catch {
      toast.error("❌ Failed to submit rating.");
    }
  };

  const handleDeleteBuild = async (buildId) => {
    if (!token) {
      toast.error("You must be logged in to delete builds.");
      return;
    }

    const confirmed = window.confirm("⚠️ Are you sure you want to delete this build?");
    if (!confirmed) {
      return;
    }

    try {
      const response = await deleteSavedBuild(buildId, token);
      toast.success(response.message || "✅ Build deleted successfully!");
      await handleViewSaved();
    } catch (error) {
      console.error(error);
      toast.error(`❌ ${error.message}`);
    }
  };

  return (
    <div className="recommender-container">
      <h2 className="recommender-title">🔧 PC Build Recommender</h2>

      <form className="recommender-form" onSubmit={handleSubmit}>
        <label>Budget (£):</label>
        <input
          type="number"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          required
          min="100"
        />

        <label>Use Case:</label>
        <select value={useCase} onChange={(e) => setUseCase(e.target.value)}>
          <option value="gaming">Gaming</option>
          <option value="general">General</option>
          <option value="work">Work</option>
          <option value="school">School</option>
        </select>

        {useCase === "gaming" && (
          <>
            <label>Game:</label>
            <input
              type="text"
              value={game}
              onChange={(e) => setGame(e.target.value)}
              placeholder="e.g., Cyberpunk 2077"
              required
            />
          </>
        )}

        <div className="recommender-buttons">
          <button type="submit" className="btn-recommend">🚀 Get Recommendation</button>
        </div>
      </form>

      {loading && <p>Loading recommendation...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {(result || savedBuilds.length > 0) && (
        <div className="recommendation-and-saved">
          {result && (
            <div className="recommended-build-card">
              <h3>🔧 Recommended Build</h3>
              <p><strong>CPU:</strong> {result.recommended_build.cpu_name}</p>
              <p><strong>GPU:</strong> {result.recommended_build.gpu_name}</p>
              <p><strong>Motherboard:</strong> {result.recommended_build.motherboard_name}</p>
              <p><strong>RAM:</strong> {result.recommended_build.ram_name}</p>
              <p><strong>Storage:</strong> {result.recommended_build.storage_name}</p>
              <p><strong>Power Supply:</strong> {result.recommended_build.psu_name}</p>
              <p><strong>Case:</strong> {result.recommended_build.case_name}</p>
              <p><strong>Total Cost:</strong> ${result.total_cost}</p>

              <div className="recommender-buttons">
                <button onClick={handleSaveBuild} className="btn-save">💾 Save This Build</button>
                <button onClick={handleViewSaved} className="btn-view-saved">📦 View Saved Builds</button>

                <h4>⭐ Rate This Build</h4>
                <StarRating rating={selectedRating} onRatingChange={setSelectedRating} />
                <button onClick={handleSubmitRating} className="btn-submit-rating">✅ Submit Rating</button>
              </div>
            </div>
          )}

          {savedBuilds.length > 0 ? (
            <div className="saved-builds-section">
              <h3>📦 Saved Builds</h3>
              {savedBuilds.map((build, index) => (
                <div className="build-card" key={index}>
                  <p><strong>CPU:</strong> {build.cpu_name}</p>
                  <p><strong>GPU:</strong> {build.gpu_name}</p>
                  <p><strong>Motherboard:</strong> {build.motherboard_name}</p>
                  <p><strong>RAM:</strong> {build.ram_name}</p>
                  <p><strong>Storage:</strong> {build.storage_name}</p>
                  <p><strong>Power Supply:</strong> {build.psu_name}</p>
                  <p><strong>Case:</strong> {build.case_name}</p>
                  <p><strong>Total Price:</strong> ${build.total_cost}</p>

                  <button
                    onClick={() => handleDeleteBuild(build.build_id)}
                    className="btn-delete-build"
                  >
                    🗑️ Delete Build
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-saved-builds">
              <p>No saved builds yet. 📭</p>
            </div>
          )}
        </div>
      )}

      <ToastContainer position="bottom-right" />
    </div>
  );
}

export default Recommender;