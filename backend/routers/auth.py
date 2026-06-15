from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_status():
    return {"status": "auth router placeholder"}
