from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.models.models import User, Career
from app.api.deps import get_current_user
from app.schemas.schemas import (
    IndustryUpdateRequest,
    IndustryUpdateResponse,
    IndustryInsightsResponse
)
from app.services.industry_intelligence_service import (
    update_career_skill_intelligence,
    get_career_industry_insights
)

router = APIRouter(prefix="/industry", tags=["Industry Skill Intelligence"])


@router.post("/update", response_model=IndustryUpdateResponse)
def trigger_industry_skill_update(
    request_data: Optional[IndustryUpdateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Triggers dynamic job-market ingestion and skill requirement updates for a career.
    Defaults to the logged-in student's target career if no career name is explicitly supplied.
    """
    career_name = None
    if request_data and request_data.career and request_data.career.strip():
        career_name = request_data.career.strip()
    elif current_user.target_career_id:
        career = db.query(Career).filter(Career.id == current_user.target_career_id).first()
        if career:
            career_name = career.name

    if not career_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please specify a career or select a target career in your profile first."
        )

    result = update_career_skill_intelligence(career_name=career_name, db=db)
    return result


@router.get("/{career_name}", response_model=IndustryInsightsResponse)
def get_industry_insights_by_career(
    career_name: str,
    db: Session = Depends(get_db)
):
    """
    Public or authenticated lookup of live industry skill intelligence,
    validated requirements, and emerging skills for a given career.
    """
    return get_career_industry_insights(career_name=career_name, db=db)


@router.get("", response_model=IndustryInsightsResponse)
def get_my_target_career_industry_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns real-time industry skill intelligence for the currently logged-in student's target career.
    """
    if not current_user.target_career_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No target career selected yet. Please choose a target career first."
        )

    career = db.query(Career).filter(Career.id == current_user.target_career_id).first()
    if not career:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target career not found."
        )

    return get_career_industry_insights(career_name=career.name, db=db)
