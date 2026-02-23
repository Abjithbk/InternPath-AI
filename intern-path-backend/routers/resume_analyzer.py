from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from services.resume_scoring import analyze_resume_text
from services.pdf_utils import extract_text
from database.schemas import ResumeAnalysisResponse

router = APIRouter(prefix="/resume", tags=["Resume"])

@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(file: UploadFile = File(...)):
    print(f"File received: {file.filename}, type: {file.content_type}", flush=True)

    file_bytes = await file.read()
    print(f"File size: {len(file_bytes)} bytes", flush=True)
    text = extract_text(file_bytes)
    print(f"Extracted text length: {len(text) if text else 0}", flush=True)

    if not text:
        return JSONResponse(
            content={"error": "Unable to extract text from PDF"},
            status_code=400
        )

    result = analyze_resume_text(text)
    print(f"Result: {result}", flush=True)
    return result