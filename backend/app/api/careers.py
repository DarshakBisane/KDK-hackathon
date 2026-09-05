from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Career, Skill, CareerSkill
from app.schemas.schemas import CareerResponse, SkillBasic

router = APIRouter(prefix="/careers", tags=["Careers"])


@router.get("", response_model=List[CareerResponse])
def get_all_careers(db: Session = Depends(get_db)):
    careers = db.query(Career).all()
    results = []
    
    for c in careers:
        skills = (
            db.query(Skill.id, Skill.name, Skill.category, CareerSkill.importance)
            .join(CareerSkill, CareerSkill.skill_id == Skill.id)
            .filter(CareerSkill.career_id == c.id)
            .all()
        )
        skill_list = [
            SkillBasic(
                id=s[0],
                name=s[1],
                category=s[2],
                importance=s[3]
            )
            for s in skills
        ]
        results.append(
            CareerResponse(
                id=c.id,
                name=c.name,
                description=c.description,
                icon=c.icon,
                category=c.category,
                required_skills=skill_list
            )
        )
    return results


@router.get("/{career_id}", response_model=CareerResponse)
def get_career_by_id(career_id: int, db: Session = Depends(get_db)):
    c = db.query(Career).filter(Career.id == career_id).first()
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Career with ID {career_id} not found."
        )

    skills = (
        db.query(Skill.id, Skill.name, Skill.category, CareerSkill.importance)
        .join(CareerSkill, CareerSkill.skill_id == Skill.id)
        .filter(CareerSkill.career_id == c.id)
        .all()
    )
    skill_list = [
        SkillBasic(
            id=s[0],
            name=s[1],
            category=s[2],
            importance=s[3]
        )
        for s in skills
    ]

    return CareerResponse(
        id=c.id,
        name=c.name,
        description=c.description,
        icon=c.icon,
        category=c.category,
        required_skills=skill_list
    )
