from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import User, Career, Skill, CareerSkill, StudentSkill
from app.schemas.schemas import SkillGapResponse


def calculate_skill_gap(user_id: int, db: Session) -> SkillGapResponse:
    """
    Calculates deterministic skill gap between the student's extracted skills
    and their selected target career's required skills.
    Formula: Readiness Score = (Matched Required Skills / Total Required Skills) * 100
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return SkillGapResponse(
            readiness_score=0.0,
            matched_skills=[],
            missing_skills=[],
            total_required_skills=0,
            total_matched_skills=0,
            student_skills_count=0
        )

    # Student skills
    student_skills_records = (
        db.query(Skill.name)
        .join(StudentSkill, StudentSkill.skill_id == Skill.id)
        .filter(StudentSkill.user_id == user_id)
        .all()
    )
    student_skill_names_set = {s[0].strip().lower(): s[0] for s in student_skills_records}
    student_skills_count = len(student_skill_names_set)

    # If no target career selected yet
    if not user.target_career_id:
        return SkillGapResponse(
            target_career_id=None,
            target_career_name=None,
            readiness_score=0.0,
            matched_skills=[],
            missing_skills=[],
            total_required_skills=0,
            total_matched_skills=0,
            student_skills_count=student_skills_count
        )

    career = db.query(Career).filter(Career.id == user.target_career_id).first()
    if not career:
        return SkillGapResponse(
            target_career_id=None,
            target_career_name=None,
            readiness_score=0.0,
            matched_skills=[],
            missing_skills=[],
            total_required_skills=0,
            total_matched_skills=0,
            student_skills_count=student_skills_count
        )

    # Get career required skills
    career_skills = (
        db.query(Skill.name, CareerSkill.importance)
        .join(CareerSkill, CareerSkill.skill_id == Skill.id)
        .filter(CareerSkill.career_id == career.id)
        .all()
    )

    matched_skills: List[str] = []
    missing_skills: List[Dict[str, str]] = []

    for skill_name, importance in career_skills:
        skill_lower = skill_name.strip().lower()
        if skill_lower in student_skill_names_set:
            matched_skills.append(skill_name)
        else:
            missing_skills.append({
                "name": skill_name,
                "importance": importance or "HIGH"
            })

    total_required = len(career_skills)
    total_matched = len(matched_skills)

    # Sort missing skills by importance (HIGH first, then MEDIUM, then LOW)
    importance_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    missing_skills.sort(key=lambda x: importance_order.get(x["importance"], 3))

    readiness_score = 0.0
    if total_required > 0:
        readiness_score = round((total_matched / total_required) * 100, 1)

    return SkillGapResponse(
        target_career_id=career.id,
        target_career_name=career.name,
        readiness_score=readiness_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        total_required_skills=total_required,
        total_matched_skills=total_matched,
        student_skills_count=student_skills_count
    )
