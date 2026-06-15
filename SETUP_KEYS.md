# API Keys & Environment Setup Guide

Follow this step-by-step guide to get all the necessary API keys and set up your local environment variables.

## 1. Get a Gemini API Key from Google AI Studio
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. On the left sidebar, click on **Get API key**.
4. Click the **Create API key** button.
5. Copy the generated key. You will need to paste this as your `GEMINI_API_KEY` in the backend environment file.

## 2. Create a Firebase Project and Get Credentials
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project** and follow the prompts to create a new project.
3. Once your project is created, click the **Gear Icon (Project settings)** in the top left next to "Project Overview".

### Set up Firestore & Auth
4. In the left sidebar under "Build", click **Authentication**, then click **Get started**. Enable the sign-in methods you want (e.g., Email/Password).
5. In the left sidebar under "Build", click **Firestore Database**, then click **Create database**. Start in test mode for local development.

### Get Backend Credentials (Service Account)
6. Go back to **Project settings** (Gear Icon) -> **Service accounts** tab.
7. Click the **Generate new private key** button. This will download a JSON file.
8. Open the JSON file. You will need:
   - `project_id` (this goes into `FIREBASE_PROJECT_ID` and `GOOGLE_CLOUD_PROJECT`)
   - `private_key` (this goes into `FIREBASE_PRIVATE_KEY`)
   - `client_email` (this goes into `FIREBASE_CLIENT_EMAIL`)

### Get Frontend Credentials (Web App Config)
9. In **Project settings** -> **General** tab, scroll down to "Your apps".
10. Click the Web icon (`</>`) to add a web app to your project. Register the app (you don't need Firebase Hosting setup right now).
11. You will be shown a `firebaseConfig` object containing keys like `apiKey`, `authDomain`, `projectId`, etc. You will use these values for your frontend `.env` file.

## 3. Copy `.env.example` to `.env` and Fill It In
You must create `.env` files from your example templates because the `.env.example` files are committed to source control (and should only contain dummy values), while `.env` files stay local to your machine.

### Backend Setup
1. Navigate to the `backend` folder: `cd backend`
2. Copy the example file to create a real `.env` file:
   - Mac/Linux: `cp .env.example .env`
   - Windows: `copy .env.example .env`
3. Open `backend/.env` in your editor and replace the placeholder values with the real keys you gathered in steps 1 and 2.

### Frontend Setup
1. Navigate to the `frontend` folder: `cd frontend`
2. Copy the example file:
   - Mac/Linux: `cp .env.example .env`
   - Windows: `copy .env.example .env`
3. Open `frontend/.env` and replace the placeholders with your Firebase Web App config values.

> **Note:** Make sure you never commit your `.env` files to GitHub or any public repository. We have already added `.env` to `.gitignore` to prevent this from happening accidentally.
