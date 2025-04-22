// Created by: Stuart Smith
// Student ID: S2336002
// Date Created: 2025-04-16
// Description:
// A star rating component for letting users rate builds visually.

import React, { useState } from "react";

function StarRating({ rating, onRatingChange }) {   
  const [hovered, setHovered] = useState(0);

  const handleMouseEnter = (index) => {
    setHovered(index);
  };

  const handleMouseLeave = () => {
    setHovered(0);
  };

  const handleClick = (index) => {
    onRatingChange(index);   
  };

  return (
    <div>
      {[1, 2, 3, 4, 5].map((index) => (
        <span
          key={index}
          style={{ fontSize: "2rem", color: (hovered || rating) >= index ? "gold" : "gray", cursor: "pointer" }}
          onMouseEnter={() => handleMouseEnter(index)}
          onMouseLeave={handleMouseLeave}
          onClick={() => handleClick(index)}
        >
          ★
        </span>
      ))}
    </div>
  );
}

export default StarRating;