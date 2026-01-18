from fastapi import APIRouter

router = APIRouter()

@router.get("/active-keywords")
def active_keywords():
    return ["software developer", "data science", "marketing"]
