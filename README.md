# Machine-Learning-Enhanced-PC-Component-Recommendation-System

Created by: Stuart Smith  
Student ID: S2336002  
Date Created: 2025-04-22

---

##  Project Overview

This project is a Machine Learning-enhanced PC component recommendation system developed as part of an Honours Project.  
It aims to assist users in selecting optimal PC components based on budget, use-case (e.g., gaming, work, general), and optional gaming goals, by intelligently suggesting complete, compatible PC builds.

Traditional tools like PCPartPicker only allow users to manually filter products.  
This project goes further by **learning from data** to provide **personalised, intelligent build recommendations**.

---

##  Technologies Used

- **Backend:**  
  - FastAPI (Python 3.11)  
  - Sklearn (Random Forest) for content-based filtering  
  - TensorFlow Recommenders (TFRS) for collaborative filtering  
  - Steam API Integration (live game requirement matching)  
  - SQLite (lightweight user data storage)

- **Frontend:**  
  - React.js (Vite-based)  
  - JWT Authentication  
  - Axios/Fetch for API interactions  
  - Toastify for notifications  

- **Deployment:**  
  - Render.com (FastAPI backend deployment)  

---

##  How to Run Locally (Optional)

> Only necessary if you want to run it locally. The project is deployed live for tutor access.

1. Clone the repository:
    ```bash
    git clone https://github.com/StuartUni/Machine-Learning-Enhanced-PC-Component-Recommendation-System.git
    ```

2. Install Python dependencies for backend:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3. Start the backend server:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

4. Install frontend dependencies and start React frontend:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

> **Note:** In `api.js`, update `API_BASE_URL` to `http://localhost:8000` when testing locally.

---

##  Live Deployment

The backend is deployed and publicly accessible:  
**Backend API:** (https://machine-learning-enhanced-pc-component.onrender.com)


To access the site: https://machine-learning-enhanced-pc-component-iyr1.onrender.com

⚡ Please Note:
The backend server is hosted on Render's free tier, which may enter sleep mode after periods of inactivity.

As a result, when first accessing the site or submitting a request (e.g., login, registration, recommendation), there may be a brief delay (10–30 seconds) while the server "wakes up."

This is normal behavior for free-tier hosting and should only occur on the first request after a period of idleness.

---
##  Acknowledgments

Special thanks to the following open-source tools and libraries:
- FastAPI
- TensorFlow Recommenders
- Scikit-learn
- React.js
- Render.com

And to all academic sources cited throughout the report.

---

