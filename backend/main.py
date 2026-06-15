from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import FRONTEND_URL
from routers import auth, jobs, resume, applications, outreach, interview

app = FastAPI(title="AI Job Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(outreach.router, prefix="/api")
app.include_router(interview.router, prefix="/api")
