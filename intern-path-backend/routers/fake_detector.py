from fastapi import APIRouter
from database.schemas import URLRequest
from ai.fake_internsip import analyze_internship

router = APIRouter()
@router.post("/detect-fake-internship")
def detect_fake(data: URLRequest):
    return analyze_internship(data.url)