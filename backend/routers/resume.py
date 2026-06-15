from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.resume_parser import parse_and_store_resume

router = APIRouter(prefix="/resume", tags=["Resume"])

@router.post("/")
async def upload_resume(user_id: str = Form(...), file: UploadFile = File(...)):
    """Uploads a master resume, parses it, and stores it in Firestore."""
    try:
        file_bytes = await file.read()
        parsed_data = parse_and_store_resume(user_id, file_bytes, file.filename)
        return parsed_data
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
