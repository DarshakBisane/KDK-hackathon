from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User
from app.schemas.schemas import DashboardResponse
from app.api.deps import get_current_user
from app.services.skill_gap_service import calculate_skill_gap

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def get_student_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    gap_result = calculate_skill_gap(current_user.id, db)

    # Compute critical gaps (missing skills with HIGH importance)
    critical_gaps = [s for s in gap_result.missing_skills if s.get("importance") == "HIGH"]
    critical_count = len(critical_gaps)

    # Generate 2-3 concrete actionable next steps
    next_steps = []
    if not current_user.target_career_id:
        next_steps.append("Select your target career goal from the Career page.")
        next_steps.append("Upload your resume to extract your current skillset.")
    elif gap_result.student_skills_count == 0:
        next_steps.append("Upload your resume to discover which required skills you already have.")
        next_steps.append(f"Explore the required skills roadmap for {gap_result.target_career_name or 'your career'}.")
    else:
        for item in gap_result.missing_skills[:2]:
            next_steps.append(f"Master {item['name']} fundamentals & complete a hands-on project.")
        if len(gap_result.missing_skills) > 2:
            next_steps.append(f"Review and track your personalized learning milestones in your Career Roadmap.")
        elif len(gap_result.missing_skills) == 0 and gap_result.total_required_skills > 0:
            next_steps.append("Congratulations! You have covered 100% of the core required skills. Keep building portfolio projects!")

    return DashboardResponse(
        user_name=current_user.name,
        student_status=current_user.student_status or "Student",
        target_career_name=gap_result.target_career_name,
        target_career_id=gap_result.target_career_id,
        readiness_score=gap_result.readiness_score,
        strong_skills_count=len(gap_result.matched_skills),
        missing_skills_count=len(gap_result.missing_skills),
        critical_gaps_count=critical_count,
        matched_skills=gap_result.matched_skills,
        missing_skills=gap_result.missing_skills,
        next_steps=next_steps
    )
