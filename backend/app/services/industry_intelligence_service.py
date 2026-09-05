from typing import Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import get_settings
from app.models.models import Career, Skill, CareerSkill, SkillEvidence
from app.data_ingestion.job_api_client import JobApiClient
from app.services.skill_intelligence_service import process_career_job_postings

settings = get_settings()


def update_career_skill_intelligence(career_name: str, db: Session) -> Dict[str, Any]:
    """
    Orchestration pipeline:
    1. Fetches live/mock job market postings for career
    2. Runs AI/rule skill extraction and canonical normalization
    3. Aggregates evidence and evaluates thresholds
    4. Dynamically updates career skill requirements
    """
    career = db.query(Career).filter(func.lower(Career.name) == career_name.strip().lower()).first()
    if not career:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Career '{career_name}' not found."
        )

    # 1. Ingest job data (external API with automatic mock fallback)
    client = JobApiClient()
    job_postings = client.get_jobs_for_career(career.name, limit=5)

    if not job_postings:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No job market data could be retrieved for career '{career_name}'."
        )

    # 2. Process intelligence and update database
    result = process_career_job_postings(career=career, job_postings=job_postings, db=db)
    return result


def get_career_industry_insights(career_name: str, db: Session) -> Dict[str, Any]:
    """
    Retrieves real-time industry skill intelligence for a career:
    - Currently validated required skills
    - Emerging/candidate skills with evidence counts
    - Evidence items supporting market demand
    """
    career = db.query(Career).filter(func.lower(Career.name) == career_name.strip().lower()).first()
    if not career:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Career '{career_name}' not found."
        )

    # 1. Required CareerSkills
    career_skills = (
        db.query(CareerSkill, Skill)
        .join(Skill, Skill.id == CareerSkill.skill_id)
        .filter(CareerSkill.career_id == career.id)
        .all()
    )

    required_skill_ids = set()
    required_skills_list = []
    for cs, s in career_skills:
        required_skill_ids.add(s.id)
        required_skills_list.append({
            "name": s.name,
            "category": s.category,
            "importance": cs.importance,
            "proficiency": cs.proficiency_required or "Intermediate",
            "confidence": cs.confidence or 0.95
        })

    # 2. Query all evidence for this career
    evidence_records = (
        db.query(SkillEvidence, Skill)
        .join(Skill, Skill.id == SkillEvidence.skill_id)
        .filter(SkillEvidence.career_id == career.id)
        .all()
    )

    # Group evidence by skill
    skill_mentions: Dict[int, Dict[str, Any]] = {}
    evidence_summary: List[Dict[str, Any]] = []

    for ev, s in evidence_records:
        if s.id not in skill_mentions:
            skill_mentions[s.id] = {
                "name": s.name,
                "category": s.category,
                "total_mentions": 0,
                "max_confidence": 0.0,
                "sources": set()
            }
        skill_mentions[s.id]["total_mentions"] += ev.mention_count
        skill_mentions[s.id]["max_confidence"] = max(skill_mentions[s.id]["max_confidence"], ev.confidence)
        skill_mentions[s.id]["sources"].add(ev.source)

        evidence_summary.append({
            "skill_name": s.name,
            "source": ev.source,
            "source_url": ev.source_url,
            "mention_count": ev.mention_count,
            "confidence": ev.confidence,
            "evidence_text": ev.evidence_text
        })

    # 3. Identify Emerging Skills (skills with evidence >= candidate_threshold, but not yet primary required CareerSkill)
    emerging_skills_list = []
    candidate_threshold = settings.JOB_INTELLIGENCE_MENTION_THRESHOLD_CANDIDATE

    for skill_id, info in skill_mentions.items():
        if skill_id not in required_skill_ids:
            emerging_skills_list.append({
                "name": info["name"],
                "category": info["category"],
                "mention_count": info["total_mentions"],
                "confidence": round(info["max_confidence"], 2),
                "is_candidate": info["total_mentions"] >= candidate_threshold,
                "sources": list(info["sources"])
            })

    # Sort emerging skills by mention count descending
    emerging_skills_list.sort(key=lambda x: x["mention_count"], reverse=True)

    return {
        "career": career.name,
        "category": career.category,
        "required_skills": required_skills_list,
        "emerging_skills": emerging_skills_list,
        "evidence_summary": evidence_summary,
        "total_evidence_items": len(evidence_summary)
    }
