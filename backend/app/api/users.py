from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User, Career, Skill, StudentSkill
from app.schemas.schemas import UserProfile, UserUpdate, TargetCareerSelect
from app.api.deps import get_current_user
from app.services.roadmap_service import generate_or_get_roadmap

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch student's extracted skills
    skills_records = (
        db.query(Skill.name)
        .join(StudentSkill, StudentSkill.skill_id == Skill.id)
        .filter(StudentSkill.user_id == current_user.id)
        .all()
    )
    skills_list = [s[0] for s in skills_records]

    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        education=current_user.education,
        student_status=current_user.student_status or "Student",
        target_career_id=current_user.target_career_id,
        target_career_name=current_user.target_career.name if current_user.target_career else None,
        skills=skills_list,
        created_at=current_user.created_at
    )


@router.put("/me", response_model=UserProfile)
def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if update_data.name is not None and update_data.name.strip():
        current_user.name = update_data.name.strip()
    if update_data.education is not None:
        current_user.education = update_data.education.strip()
    if update_data.student_status is not None:
        current_user.student_status = update_data.student_status.strip()
    if update_data.target_career_id is not None:
        career = db.query(Career).filter(Career.id == update_data.target_career_id).first()
        if career:
            current_user.target_career_id = career.id
            # Refresh roadmap for new career
            db.commit()
            generate_or_get_roadmap(current_user.id, db)

    db.commit()
    db.refresh(current_user)

    # Fetch updated skills
    skills_records = (
        db.query(Skill.name)
        .join(StudentSkill, StudentSkill.skill_id == Skill.id)
        .filter(StudentSkill.user_id == current_user.id)
        .all()
    )
    skills_list = [s[0] for s in skills_records]

    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        education=current_user.education,
        student_status=current_user.student_status,
        target_career_id=current_user.target_career_id,
        target_career_name=current_user.target_career.name if current_user.target_career else None,
        skills=skills_list,
        created_at=current_user.created_at
    )


@router.post("/target-career", response_model=UserProfile)
def select_target_career(
    target_data: TargetCareerSelect,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    career = db.query(Career).filter(Career.id == target_data.career_id).first()
    if not career:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target career with id {target_data.career_id} not found."
        )

    current_user.target_career_id = career.id
    db.commit()
    db.refresh(current_user)

    # Re-generate roadmap items for this career's gaps
    generate_or_get_roadmap(current_user.id, db)

    skills_records = (
        db.query(Skill.name)
        .join(StudentSkill, StudentSkill.skill_id == Skill.id)
        .filter(StudentSkill.user_id == current_user.id)
        .all()
    )
    skills_list = [s[0] for s in skills_records]

    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        education=current_user.education,
        student_status=current_user.student_status,
        target_career_id=current_user.target_career_id,
        target_career_name=career.name,
        skills=skills_list,
        created_at=current_user.created_at
    )
