import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL

def initialize_firebase():
    # Check if firebase is already initialized to prevent hot-reload crash
    if not firebase_admin._apps:
        if not FIREBASE_PROJECT_ID or not FIREBASE_PRIVATE_KEY or not FIREBASE_CLIENT_EMAIL:
            print("Warning: Firebase environment variables are missing. Firebase won't initialize properly.")
            return

        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": FIREBASE_PROJECT_ID,
            "private_key": FIREBASE_PRIVATE_KEY,
            "client_email": FIREBASE_CLIENT_EMAIL,
            "token_uri": "https://oauth2.googleapis.com/token",
        })
        
        firebase_admin.initialize_app(cred)

# Initialize on module load
initialize_firebase()

# Expose Firestore client
db = firestore.client() if firebase_admin._apps else None

# Note: The database uses the following top-level collections:
# - users -> stores user profile info
# - resumes -> stores uploaded and parsed resumes
# - jobs -> stores discovered job listings
# - applications -> stores application status and tailored documents
