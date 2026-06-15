from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from services.firebase_service import db
from services.gemini_service import generate_interview_questions, evaluate_mock_answer

router = APIRouter(prefix="/interview", tags=["Interview"])

class QuestionsRequest(BaseModel):
    user_id: str
    resume_id: str

class MockAnswerRequest(BaseModel):
    user_id: str
    question: str
    answer: str
    job_title: str
    company_name: str
    skill_being_tested: str

@router.post("/{job_id}/questions")
def get_interview_questions(job_id: str, req: QuestionsRequest):
    """Generates 20 targeted interview questions based on the job and resume."""
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    # Fetch job
    job_ref = db.collection("jobs").document(job_id)
    job_doc = job_ref.get()
    if not job_doc.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = job_doc.to_dict()
    
    # Fetch Resume
    resume_ref = db.collection("resumes").document(req.resume_id)
    resume_doc = resume_ref.get()
    if not resume_doc.exists:
        raise HTTPException(status_code=404, detail="Resume not found")
    resume_data = resume_doc.to_dict()
    
    if resume_data.get("user_id") != req.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to access this resume")
        
    try:
        questions = generate_interview_questions(
            user_id=req.user_id,
            job_description=job_data.get("description", ""),
            job_title=job_data.get("title", ""),
            tailored_resume=resume_data.get("raw_text", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Question generation error: {str(e)}")
        
    # Save to application document
    app_query = db.collection("applications").where("user_id", "==", req.user_id).where("job_id", "==", job_id).stream()
    app_docs = list(app_query)
    
    update_data = {
        "interview_questions": questions,
        "last_updated": datetime.now(timezone.utc)
    }
    
    if app_docs:
        db.collection("applications").document(app_docs[0].id).update(update_data)
    else:
        update_data.update({
            "user_id": req.user_id,
            "job_id": job_id,
            "job_title": job_data.get("title"),
            "company": job_data.get("company"),
            "status": "interviewing",
            "created_at": datetime.now(timezone.utc)
        })
        db.collection("applications").add(update_data)
        
    return {"questions": questions}

@router.post("/mock-answer")
def submit_mock_answer(req: MockAnswerRequest):
    """Evaluates a candidate's answer to an interview question. Does not save state."""
    try:
        evaluation = evaluate_mock_answer(
            user_id=req.user_id,
            interview_question=req.question,
            candidate_answer=req.answer,
            job_title=req.job_title,
            company_name=req.company_name,
            skill_being_tested=req.skill_being_tested
        )
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Evaluation error: {str(e)}")
