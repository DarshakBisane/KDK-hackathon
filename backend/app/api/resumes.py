from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User
from app.schemas.schemas import ResumeAnalyzeResponse
from app.api.deps import get_current_user
from app.services.resume_service import process_and_analyze_resume

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension and MIME type
    filename = file.filename or "resume.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files (.pdf) are supported. Please upload a PDF resume."
        )

    # 2. Read bytes with size limit (max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 10MB limit. Please upload a smaller PDF file."
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF file is empty. Please select a valid resume."
        )

    # 3. Process and extract skills via pipeline
    result = await process_and_analyze_resume(
        file_bytes=content,
        filename=filename,
        user_id=current_user.id,
        db=db
    )

    return result
