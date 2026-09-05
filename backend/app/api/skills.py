from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User, Skill, StudentSkill
from app.schemas.schemas import SkillGapResponse
from app.api.deps import get_current_user
from app.services.skill_gap_service import calculate_skill_gap

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("/gap", response_model=SkillGapResponse)
def get_user_skill_gap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes the deterministic skill gap for the current student.
    Returns matched skills, missing skills grouped by importance, and readiness score.
    """
    return calculate_skill_gap(current_user.id, db)


@router.get("/user", response_model=List[str])
def get_user_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the list of currently recognized skills for the student.
    """
    skills_records = (
        db.query(Skill.name)
        .join(StudentSkill, StudentSkill.skill_id == Skill.id)
        .filter(StudentSkill.user_id == current_user.id)
        .all()
    )
    return [s[0] for s in skills_records]
