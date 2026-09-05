from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import User, Skill, StudentSkill, Resume
from app.schemas.schemas import ResumeAnalyzeResponse, ResumeExtraction
from app.utils.pdf_extractor import extract_text_from_pdf
from app.services.gemini_service import extract_resume_info
from app.services.normalization_service import normalize_skills_list
from app.services.skill_gap_service import calculate_skill_gap
from app.services.roadmap_service import generate_or_get_roadmap


async def process_and_analyze_resume(
    file_bytes: bytes,
    filename: str,
    user_id: int,
    db: Session
) -> ResumeAnalyzeResponse:
    """
    Complete resume processing pipeline:
    PDF -> Text Extraction -> Gemini Structured Extraction -> Pydantic Validation
    -> Skill Normalization -> Save Student Skills -> Compute Skill Gap -> Update Roadmap -> Return
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student user account not found."
        )

    # 1. Extract text from PDF
    extracted_text = extract_text_from_pdf(file_bytes)

    # 2. Extract structured data via Gemini AI
    extracted_data: ResumeExtraction = await extract_resume_info(extracted_text)

    # 3. Normalize skill names
    raw_skills = extracted_data.skills
    normalized_skills = normalize_skills_list(raw_skills)

    # 4. Save/Update extracted student skills in database
    for skill_name in normalized_skills:
        # Get or create global Skill record
        skill = db.query(Skill).filter(Skill.name == skill_name).first()
        if not skill:
            skill = Skill(name=skill_name, category="Detected Skill")
            db.add(skill)
            db.flush()

        # Check if student already has this skill
        student_skill = (
            db.query(StudentSkill)
            .filter(
                StudentSkill.user_id == user_id,
                StudentSkill.skill_id == skill.id
            )
            .first()
        )
        if not student_skill:
            student_skill = StudentSkill(
                user_id=user_id,
                skill_id=skill.id,
                proficiency="detected",
                source="resume"
            )
            db.add(student_skill)

    # 5. Optionally update user education if detected
    if extracted_data.education and len(extracted_data.education) > 0:
        first_edu = str(extracted_data.education[0]).strip()
        if first_edu and (not user.education or user.education == "B.Tech Computer Science"):
            user.education = first_edu[:180]

    # 6. Save Resume audit record
    resume_record = Resume(
        user_id=user_id,
        filename=filename,
        file_size=len(file_bytes),
        extracted_data=extracted_data.model_dump()
    )
    db.add(resume_record)
    db.commit()

    # 7. Recalculate skill gap & refresh roadmap if user has a target career
    gap_result = calculate_skill_gap(user_id, db)
    if user.target_career_id:
        generate_or_get_roadmap(user_id, db)

    return ResumeAnalyzeResponse(
        message="Resume analyzed and skills successfully extracted!",
        extracted_skills_count=len(normalized_skills),
        extracted_skills=normalized_skills,
        readiness_score=gap_result.readiness_score if user.target_career_id else None,
        target_career=gap_result.target_career_name
    )
