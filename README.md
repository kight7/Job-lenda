# AI Job Applier Agent

This project is an automated AI-powered agent designed to help search, score, tailor resumes, and apply for jobs. Below is a breakdown of the project's structure and what each folder is responsible for:

## Project Structure

### `backend/`
Contains the Python FastAPI backend which handles all the core logic, database interactions, and AI processing.
- **`routers/`**: API endpoints for different features (jobs, resumes, applications, etc.).
- **`services/`**: Core business logic and integrations (e.g., Gemini AI, web scrapers, Firebase, email).
- **`models/`**: Data structures and schemas representing jobs, users, and applications.
- **`utils/`**: Helper functions for rate limiting, privacy processing, and ATS (Applicant Tracking System) compatibility.
- **`prompts/`**: Text files containing the specific system prompts sent to the AI (e.g., for scoring fit, tailoring resumes, or generating cover letters).

### `frontend/`
Contains the React frontend application for the user interface.
- **`public/`**: Static assets like `index.html` and images.
- **`src/pages/`**: The main views or screens of the application (Dashboard, Job Search, Resume Tailor, etc.).
- **`src/components/`**: Reusable UI elements (Navigation bar, Job cards, badges, loading spinners, etc.).
- **`src/services/`**: Functions that handle communicating with the backend API and Firebase auth/database.
- **`src/styles/`**: Global CSS and styling rules.

### `docker/`
Contains files related to containerizing the application for deployment (like the Dockerfile).

### Root Files
- **`.gitignore`**: Specifies intentionally untracked files that Git should ignore.
- **`README.md`**: This file, providing an overview of the project.
