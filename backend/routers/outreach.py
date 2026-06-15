from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from services.firebase_service import db
from services.gemini_service import draft_outreach_message

router = APIRouter(prefix="/outreach", tags=["Outreach"])

class DraftRequest(BaseModel):
    user_id: str
    job_id: str
    channel: str # "email" or "linkedin"
    recruiter_name: Optional[str] = "Hiring Manager"

class ApproveRequest(BaseModel):
    user_id: str
    edited_message: Optional[str] = None

@router.post("/draft")
def draft_outreach(req: DraftRequest):
    """Drafts an outreach message using Gemini and saves it to the application."""
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    if req.channel not in ["email", "linkedin"]:
        raise HTTPException(status_code=400, detail="Channel must be 'email' or 'linkedin'")
        
    # 1. Fetch Job
    job_ref = db.collection("jobs").document(req.job_id)
    job_doc = job_ref.get()
    if not job_doc.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = job_doc.to_dict()
    
    # 2. Fetch User Profile
    user_ref = db.collection("users").document(req.user_id)
    user_doc = user_ref.get()
    
    candidate_name = "Candidate"
    candidate_highlights = "Experienced professional looking for new opportunities."
    
    if user_doc.exists:
        user_data = user_doc.to_dict()
        candidate_name = user_data.get("name", candidate_name)
        candidate_highlights = user_data.get("highlights", candidate_highlights)
    
    # 3. Call Gemini
    try:
        draft = draft_outreach_message(
            user_id=req.user_id,
            candidate_name=candidate_name,
            job_title=job_data.get("title", ""),
            company_name=job_data.get("company", ""),
            recruiter_name=req.recruiter_name,
            channel=req.channel,
            candidate_highlights=candidate_highlights
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Draft error: {str(e)}")
        
    # 4. Save to Application Document
    app_query = db.collection("applications").where("user_id", "==", req.user_id).where("job_id", "==", req.job_id).stream()
    app_docs = list(app_query)
    
    outreach_data = {
        "outreach_message": draft.get("message"),
        "outreach_subject": draft.get("subject"),
        "outreach_status": "draft",
        "last_updated": datetime.now(timezone.utc)
    }
    
    if app_docs:
        db.collection("applications").document(app_docs[0].id).update(outreach_data)
    else:
        outreach_data.update({
            "user_id": req.user_id,
            "job_id": req.job_id,
            "job_title": job_data.get("title"),
            "company": job_data.get("company"),
            "status": "discovered",
            "created_at": datetime.now(timezone.utc)
        })
        db.collection("applications").add(outreach_data)
        
    # 5. Return draft
    return {
        "subject": draft.get("subject"),
        "message": draft.get("message"),
        "status": "draft — not sent"
    }

@router.post("/{application_id}/approve")
def approve_outreach(application_id: str, req: ApproveRequest):
    """Marks a drafted outreach message as approved."""
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    app_ref = db.collection("applications").document(application_id)
    app_doc = app_ref.get()
    if not app_doc.exists:
        raise HTTPException(status_code=404, detail="Application not found")
        
    if app_doc.to_dict().get("user_id") != req.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    update_data = {
        "outreach_status": "approved",
        "outreach_approved_at": datetime.now(timezone.utc),
        "last_updated": datetime.now(timezone.utc)
    }
    
    if req.edited_message is not None:
        update_data["outreach_message"] = req.edited_message
        
    try:
        app_ref.update(update_data)
        return {"message": "Outreach approved successfully. Not automatically sent."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving outreach: {str(e)}")
