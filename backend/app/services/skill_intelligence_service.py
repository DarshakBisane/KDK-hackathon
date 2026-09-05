import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import get_settings
from app.models.models import Career, Skill, CareerSkill, SkillEvidence, SkillAlias, utc_now
from app.services.normalization_service import normalize_skill_name, normalize_skills_list
from app.data_ingestion.job_api_client import JobPosting

logger = logging.getLogger("skillgap.intelligence")
settings = get_settings()


def process_career_job_postings(
    career: Career,
    job_postings: List[JobPosting],
    db: Session,
    candidate_threshold: int = None,
    required_threshold: int = None
) -> Dict[str, Any]:
    """
    High-performance batch processor for job postings:
    1. Aggregates skill mentions and metadata across postings in memory
    2. Bulk loads and reconciles Skills, Aliases, Evidence, and CareerSkills
    3. Promotes candidate skills to CareerSkill if mention_count >= required_threshold (5)
    4. Executes single-transaction commit
    """
    if candidate_threshold is None:
        candidate_threshold = settings.JOB_INTELLIGENCE_MENTION_THRESHOLD_CANDIDATE
    if required_threshold is None:
        required_threshold = settings.JOB_INTELLIGENCE_MENTION_THRESHOLD_REQUIRED

    # Step 1: In-memory aggregation across jobs
    skill_batch_stats: Dict[str, Dict[str, Any]] = {}

    for job in job_postings:
        raw_skills = job.explicit_skills if job.explicit_skills else normalize_skills_list([job.title])
        # Deduplicate within same job posting
        seen_in_job = set()
        for raw in raw_skills:
            if not raw or not raw.strip():
                continue
            cleaned = raw.strip()
            norm = normalize_skill_name(cleaned)
            norm_lower = norm.lower()

            if norm_lower not in skill_batch_stats:
                skill_batch_stats[norm_lower] = {
                    "canonical_name": norm,
                    "raw_aliases": set([cleaned]),
                    "mention_count": 0,
                    "source": job.source,
                    "url": job.url,
                    "sample_text": job.description[:350] if job.description else f"Mentioned in {job.title}"
                }
            else:
                skill_batch_stats[norm_lower]["raw_aliases"].add(cleaned)

            if norm_lower not in seen_in_job:
                skill_batch_stats[norm_lower]["mention_count"] += 1
                seen_in_job.add(norm_lower)

    if not skill_batch_stats:
        return {
            "career": career.name,
            "jobs_processed": len(job_postings),
            "skills_detected": [],
            "new_skills": [],
            "updated_requirements": [],
            "status": "success"
        }

    # Step 2: Bulk load existing Skills & Aliases
    existing_skills = db.query(Skill).all()
    skill_by_lower = {s.name.lower(): s for s in existing_skills}

    existing_aliases = db.query(SkillAlias).all()
    alias_map = {a.alias.lower(): a.skill_id for a in existing_aliases}

    # Bulk load existing CareerSkills for this career
    existing_career_skills = db.query(CareerSkill).filter(CareerSkill.career_id == career.id).all()
    career_skills_map = {cs.skill_id: cs for cs in existing_career_skills}

    # Bulk load existing SkillEvidence for this career
    existing_evidence = db.query(SkillEvidence).filter(SkillEvidence.career_id == career.id).all()
    evidence_map = {ev.skill_id: ev for ev in existing_evidence}

    newly_created_skills: List[str] = []
    promoted_career_skills: List[str] = []
    all_detected_skill_names: List[str] = []

    # Step 3: Reconcile each skill
    for norm_lower, stats in skill_batch_stats.items():
        canonical_name = stats["canonical_name"]
        all_detected_skill_names.append(canonical_name)

        # 3a. Find or create Skill instance
        skill = skill_by_lower.get(norm_lower)
        if not skill and norm_lower in alias_map:
            s_id = alias_map[norm_lower]
            skill = next((s for s in existing_skills if s.id == s_id), None)

        if not skill:
            skill = Skill(
                name=canonical_name,
                category=career.category,
                first_detected_at=utc_now(),
                last_updated_at=utc_now(),
                created_at=utc_now(),
                updated_at=utc_now()
            )
            db.add(skill)
            db.flush()
            skill_by_lower[norm_lower] = skill
            newly_created_skills.append(canonical_name)

        # 3b. Register aliases
        for alias_term in stats["raw_aliases"]:
            if alias_term.lower() != skill.name.lower() and alias_term.lower() not in alias_map:
                alias_obj = SkillAlias(
                    skill_id=skill.id,
                    alias=alias_term,
                    source="normalization_auto"
                )
                db.add(alias_obj)
                alias_map[alias_term.lower()] = skill.id

        # 3c. Update or create SkillEvidence
        evidence = evidence_map.get(skill.id)
        if evidence:
            evidence.mention_count += stats["mention_count"]
            evidence.detected_at = utc_now()
            evidence.confidence = min(round(0.80 + (evidence.mention_count * 0.03), 2), 0.99)
        else:
            evidence = SkillEvidence(
                skill_id=skill.id,
                career_id=career.id,
                source=stats["source"],
                source_url=stats["url"],
                evidence_text=stats["sample_text"],
                mention_count=stats["mention_count"],
                confidence=min(round(0.80 + (stats["mention_count"] * 0.03), 2), 0.99),
                detected_at=utc_now(),
                created_at=utc_now()
            )
            db.add(evidence)
            evidence_map[skill.id] = evidence

        # 3d. Check promotion threshold for CareerSkill
        total_mentions = evidence.mention_count
        if total_mentions >= required_threshold:
            career_skill = career_skills_map.get(skill.id)
            if not career_skill:
                career_skill = CareerSkill(
                    career_id=career.id,
                    skill_id=skill.id,
                    importance="HIGH" if total_mentions >= 7 else "MEDIUM",
                    proficiency_required="Intermediate",
                    confidence=min(round(0.80 + (total_mentions * 0.03), 2), 0.99),
                    last_updated_at=utc_now()
                )
                db.add(career_skill)
                career_skills_map[skill.id] = career_skill
                if canonical_name not in promoted_career_skills:
                    promoted_career_skills.append(canonical_name)
            else:
                career_skill.confidence = min(round(0.80 + (total_mentions * 0.03), 2), 0.99)
                career_skill.last_updated_at = utc_now()

    db.commit()

    return {
        "career": career.name,
        "jobs_processed": len(job_postings),
        "skills_detected": sorted(list(set(all_detected_skill_names))),
        "new_skills": newly_created_skills,
        "updated_requirements": promoted_career_skills,
        "status": "success"
    }
