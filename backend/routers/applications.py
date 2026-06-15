from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
from services.firebase_service import db

router = APIRouter(prefix="/applications", tags=["Applications"])

class StatusUpdateRequest(BaseModel):
    user_id: str
    new_status: str

class NotesUpdateRequest(BaseModel):
    user_id: str
    notes: str

VALID_STATUSES = [
    "discovered", "shortlisted", "resume_tailored", 
    "applied", "interviewing", "offered", "rejected"
]

@router.get("/{user_id}")
def get_applications(user_id: str):
    """Returns all applications for the user."""
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    try:
        apps_query = db.collection("applications").where("user_id", "==", user_id).stream()
        applications = []
        for doc in apps_query:
            app_data = doc.to_dict()
            app_data["application_id"] = doc.id
            applications.append(app_data)
        
        # Sort by last updated
        applications.sort(key=lambda x: x.get("last_updated", x.get("created_at", "")), reverse=True)
        return {"applications": applications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching applications: {str(e)}")

@router.patch("/{application_id}/status")
def update_status(application_id: str, req: StatusUpdateRequest):
    """Updates the status of an application."""
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    if req.new_status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
        
    app_ref = db.collection("applications").document(application_id)
    app_doc = app_ref.get()
    if not app_doc.exists:
        raise HTTPException(status_code=404, detail="Application not found")
        
    if app_doc.to_dict().get("user_id") != req.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    try:
        app_ref.update({
            "status": req.new_status,
            "last_updated": datetime.now(timezone.utc)
        })
        return {"message": "Status updated successfully", "new_status": req.new_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")

@router.patch("/{application_id}/notes")
def update_notes(application_id: str, req: NotesUpdateRequest):
    """Saves free-text notes to the application."""
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    app_ref = db.collection("applications").document(application_id)
    app_doc = app_ref.get()
    if not app_doc.exists:
        raise HTTPException(status_code=404, detail="Application not found")
        
    if app_doc.to_dict().get("user_id") != req.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    try:
        app_ref.update({
            "notes": req.notes,
            "last_updated": datetime.now(timezone.utc)
        })
        return {"message": "Notes updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notes: {str(e)}")
