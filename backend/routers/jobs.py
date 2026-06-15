from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from services.firebase_service import db
from services.scraper_service import scrape_jobs
from services.gemini_service import score_job_fit, tailor_resume, generate_cover_letter

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# --- Pydantic Models for Input Validation ---
class JobSearchRequest(BaseModel):
    keywords: str
    location: str
    user_id: str
    resume_id: str

class TailorRequest(BaseModel):
    user_id: str
    resume_id: str

class CoverLetterRequest(BaseModel):
    user_id: str
    resume_id: str
    tone: str = "formal"

# --- Endpoints ---

@router.post("/search")
def search_jobs(req: JobSearchRequest):
    """
    Scrapes jobs based on keywords, scores them against the user's resume,
    and stores them in Firestore.
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    # 1. Fetch the user's resume text from Firestore
    if req.resume_id == "default_resume_id":
        resume_text = "Experienced Financial Analyst with 5 years of experience in corporate finance, financial modeling, forecasting, and data analysis using Python, SQL, and Excel. Strong background in accounting. Based in Mumbai."
    else:
        resume_ref = db.collection("resumes").document(req.resume_id)
        resume_doc = resume_ref.get()
        if not resume_doc.exists:
            raise HTTPException(status_code=404, detail="Resume not found. Please upload a resume first.")
            
        resume_data = resume_doc.to_dict()
        if resume_data.get("user_id") != req.user_id:
            raise HTTPException(status_code=403, detail="Unauthorized to access this resume.")
            
        resume_text = resume_data.get("raw_text", "")
        if not resume_text:
            raise HTTPException(status_code=400, detail="The provided resume is empty.")
        
    # 2. Call the scraper service
    try:
        scraped_jobs = scrape_jobs(req.keywords, req.location, max_results=15)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job scraper failed: {str(e)}")
        
    if not scraped_jobs:
        return {"jobs": [], "total": 0}
        
    # 3 & 4. Call score_job_fit for each job and attach scores
    scored_jobs = []
    for job in scraped_jobs:
        try:
            fit_result = score_job_fit(
                user_id=req.user_id, 
                resume_text=resume_text, 
                job_description=job["description"], 
                company_name=job["company"]
            )
            # Attach score and breakdown to the job dict
            job.update(fit_result)
            job["user_id"] = req.user_id
            job["resume_id"] = req.resume_id
            job["discovered_at"] = datetime.now(timezone.utc)
            
            # 5. Save to Firestore
            job_ref = db.collection("jobs").document()
            job["job_id"] = job_ref.id
            job_ref.set(job)
            
            scored_jobs.append(job)
        except Exception as e:
            print(f"Skipping job '{job['title']}' due to AI scoring error: {e}")
            continue
            
    # 6. Sort by fit_score descending
    scored_jobs.sort(key=lambda x: x.get("fit_score", 0), reverse=True)
    
    return {"jobs": scored_jobs, "total": len(scored_jobs)}

@router.get("/{user_id}")
def get_user_jobs(user_id: str):
    """
    Returns all jobs previously discovered and scored for this user.
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    try:
        jobs_query = db.collection("jobs").where("user_id", "==", user_id).stream()
        jobs = [doc.to_dict() for doc in jobs_query]
        # Sort jobs by fit_score descending
        jobs.sort(key=lambda x: x.get("fit_score", 0), reverse=True)
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {str(e)}")

@router.post("/{job_id}/tailor")
def tailor_job_resume(job_id: str, req: TailorRequest):
    """
    Tailors the user's resume for a specific job and saves it to an Application document.
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    # 1. Fetch job description
    job_ref = db.collection("jobs").document(job_id)
    job_doc = job_ref.get()
    if not job_doc.exists:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job_data = job_doc.to_dict()
    if job_data.get("user_id") != req.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this job.")
        
    # 2. Fetch resume text
    if req.resume_id == "default_resume_id":
        resume_text = "Experienced Financial Analyst with 5 years of experience in corporate finance, financial modeling, forecasting, and data analysis using Python, SQL, and Excel. Strong background in accounting. Based in Mumbai."
    else:
        resume_ref = db.collection("resumes").document(req.resume_id)
        resume_doc = resume_ref.get()
        if not resume_doc.exists:
            raise HTTPException(status_code=404, detail="Resume not found")
        resume_data = resume_doc.to_dict()
        resume_text = resume_data.get("raw_text", "")
    
    # 3. Call AI tailor_resume
    try:
        tailor_result = tailor_resume(
            user_id=req.user_id,
            original_resume=resume_data.get("raw_text", ""),
            job_description=job_data.get("description", ""),
            job_title=job_data.get("title", ""),
            company_name=job_data.get("company", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Tailoring failed: {str(e)}")
        
    # 4. Save to applications collection
    app_query = db.collection("applications").where("user_id", "==", req.user_id).where("job_id", "==", job_id).stream()
    app_docs = list(app_query)
    
    app_data_update = {
        "tailored_resume": tailor_result.get("tailored_resume"),
        "changes_made": tailor_result.get("changes_made", []),
        "updated_at": datetime.now(timezone.utc)
    }
    
    if app_docs:
        # Update existing application document
        db.collection("applications").document(app_docs[0].id).update(app_data_update)
    else:
        # Create new application document
        app_data_update.update({
            "user_id": req.user_id,
            "job_id": job_id,
            "resume_id": req.resume_id,
            "status": "Preparing",
            "created_at": datetime.now(timezone.utc)
        })
        db.collection("applications").add(app_data_update)
        
    # 5. Return tailored resume
    return tailor_result

@router.post("/{job_id}/cover-letter")
def create_cover_letter(job_id: str, req: CoverLetterRequest):
    """
    Generates a cover letter for a specific job and saves it to an Application document.
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    # Fetch job description
    job_ref = db.collection("jobs").document(job_id)
    job_doc = job_ref.get()
    if not job_doc.exists:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job_data = job_doc.to_dict()
    if job_data.get("user_id") != req.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this job.")
        
    # Fetch resume summary (fall back to raw text if summary missing)
    if req.resume_id == "default_resume_id":
        resume_summary = "Experienced Financial Analyst with 5 years of experience in corporate finance, financial modeling, forecasting, and data analysis using Python, SQL, and Excel. Strong background in accounting. Based in Mumbai."
    else:
        resume_ref = db.collection("resumes").document(req.resume_id)
        resume_doc = resume_ref.get()
        if not resume_doc.exists:
            raise HTTPException(status_code=404, detail="Resume not found")
            
        resume_data = resume_doc.to_dict()
        resume_summary = resume_data.get("summary")
        if not resume_summary:
            resume_summary = resume_data.get("raw_text", "")[:1500] # Fallback snippet
        
    # Call AI generate_cover_letter
    try:
        cl_result = generate_cover_letter(
            user_id=req.user_id,
            resume_summary=resume_summary,
            job_description=job_data.get("description", ""),
            job_title=job_data.get("title", ""),
            company_name=job_data.get("company", ""),
            tone=req.tone
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Cover letter generation failed: {str(e)}")
        
    # Save to applications collection
    app_query = db.collection("applications").where("user_id", "==", req.user_id).where("job_id", "==", job_id).stream()
    app_docs = list(app_query)
    
    app_data_update = {
        "cover_letter": cl_result.get("cover_letter"),
        "updated_at": datetime.now(timezone.utc)
    }
    
    if app_docs:
        # Update existing application
        db.collection("applications").document(app_docs[0].id).update(app_data_update)
    else:
        # Create new application
        app_data_update.update({
            "user_id": req.user_id,
            "job_id": job_id,
            "resume_id": req.resume_id,
            "status": "Preparing",
            "created_at": datetime.now(timezone.utc)
        })
        db.collection("applications").add(app_data_update)
        
    return cl_result
