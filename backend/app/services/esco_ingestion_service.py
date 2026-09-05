import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.models.models import Occupation, Skill, OccupationSkill, utc_now
from app.services.esco_service import esco_client

logger = logging.getLogger("skillgap.esco.ingestion")


class EscoIngestionService:
    """
    Ingestion service for official European Commission ESCO occupations and skills.
    Fetches occupation structures, extracts essential and optional skills,
    and synchronizes them into PostgreSQL with idempotent upsert handling.
    """

    def __init__(self, client=None):
        self.client = client or esco_client

    async def ingest_occupation_by_search_async(
        self,
        db: Session,
        query: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Searches ESCO for an occupation query and ingests the top matching occupation.
        """
        logger.info(f"Ingesting ESCO occupation by search query: '{query}'")
        search_res = await self.client.search_occupations_async(query=query, limit=5, language=language)
        occupations = search_res.get("occupations", [])

        if not occupations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No ESCO occupations found matching query '{query}'."
            )

        # Select the best matching occupation URI (first result)
        target_occupation = occupations[0]
        esco_uri = target_occupation["uri"]
        logger.info(f"Matched query '{query}' to ESCO occupation '{target_occupation['title']}' ({esco_uri})")

        return await self.ingest_occupation_by_uri_async(db=db, esco_uri=esco_uri, language=language)

    async def ingest_occupation_by_uri_async(
        self,
        db: Session,
        esco_uri: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Fetches full ESCO occupation resource for the given URI, extracts its essential
        and optional skills, and upserts them into PostgreSQL.
        """
        if not esco_uri or not esco_uri.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ESCO occupation URI cannot be empty."
            )

        esco_uri = esco_uri.strip()
        logger.info(f"Starting ESCO ingestion for occupation URI: {esco_uri}")

        # 1. Fetch complete occupation resource from official ESCO API
        occ_data = await self.client.get_occupation_details_async(uri=esco_uri, language=language)

        title = occ_data.get("title", "").strip()
        code = occ_data.get("code")
        description = occ_data.get("description", "")
        essential_skills_raw = occ_data.get("essential_skills", [])
        optional_skills_raw = occ_data.get("optional_skills", [])

        try:
            # 2. Upsert Occupation record
            occupation = db.query(Occupation).filter(Occupation.esco_uri == esco_uri).first()
            if not occupation:
                occupation = Occupation(
                    esco_uri=esco_uri,
                    title=title,
                    code=code,
                    description=description,
                    language=language,
                    created_at=utc_now(),
                    updated_at=utc_now()
                )
                db.add(occupation)
                db.flush()
                logger.info(f"Created new Occupation in DB: '{title}' (ID: {occupation.id})")
            else:
                occupation.title = title
                occupation.code = code
                occupation.description = description
                occupation.language = language
                occupation.updated_at = utc_now()
                db.flush()
                logger.info(f"Updated existing Occupation in DB: '{title}' (ID: {occupation.id})")

            # 3. Gather all skills from essential and optional lists
            all_raw_skills = []
            for item in essential_skills_raw:
                all_raw_skills.append({**item, "relation_type": "essential"})
            for item in optional_skills_raw:
                all_raw_skills.append({**item, "relation_type": "optional"})

            # Extract distinct URIs and names for batch querying
            skill_uris = [s["uri"] for s in all_raw_skills if s.get("uri")]
            skill_titles = [s["title"] for s in all_raw_skills if s.get("title")]

            # Batch query existing skills by URI and by title/name
            existing_by_uri = {}
            if skill_uris:
                for s in db.query(Skill).filter(Skill.esco_uri.in_(skill_uris)).all():
                    existing_by_uri[s.esco_uri] = s

            existing_by_name = {}
            if skill_titles:
                for s in db.query(Skill).filter(
                    or_(Skill.name.in_(skill_titles), Skill.title.in_(skill_titles))
                ).all():
                    existing_by_name[s.name.lower()] = s
                    if s.title:
                        existing_by_name[s.title.lower()] = s

            # 4. Process each skill (Upsert into Skill table)
            skill_map: Dict[str, Skill] = {}  # uri -> Skill model instance
            new_skills_to_add = []

            for raw_skill in all_raw_skills:
                s_uri = raw_skill.get("uri", "").strip()
                s_title = raw_skill.get("title", "").strip()
                s_type = raw_skill.get("skill_type", "skill")
                if not s_title:
                    continue

                matched_skill = existing_by_uri.get(s_uri)
                if not matched_skill:
                    matched_skill = existing_by_name.get(s_title.lower())

                if matched_skill:
                    # Update metadata on existing skill
                    if not matched_skill.esco_uri:
                        matched_skill.esco_uri = s_uri
                    matched_skill.title = s_title
                    if not matched_skill.skill_type:
                        matched_skill.skill_type = s_type
                    if not matched_skill.language:
                        matched_skill.language = language
                    matched_skill.updated_at = utc_now()
                    skill_map[s_uri] = matched_skill
                else:
                    # Create new Skill
                    new_skill = Skill(
                        esco_uri=s_uri if s_uri else None,
                        name=s_title,
                        title=s_title,
                        category="ESCO " + s_type.capitalize() if s_type else "General",
                        skill_type=s_type,
                        language=language,
                        created_at=utc_now(),
                        updated_at=utc_now(),
                        first_detected_at=utc_now(),
                        last_updated_at=utc_now()
                    )
                    db.add(new_skill)
                    new_skills_to_add.append(new_skill)
                    skill_map[s_uri] = new_skill
                    # Register in lookup cache to avoid intra-batch duplicates
                    if s_uri:
                        existing_by_uri[s_uri] = new_skill
                    existing_by_name[s_title.lower()] = new_skill

            if new_skills_to_add:
                db.flush()
                logger.info(f"Added {len(new_skills_to_add)} new skills into database.")

            # 5. Upsert OccupationSkill relationships
            existing_relations = db.query(OccupationSkill).filter(
                OccupationSkill.occupation_id == occupation.id
            ).all()
            rel_by_skill_id = {r.skill_id: r for r in existing_relations}

            essential_count = 0
            optional_count = 0

            for raw_skill in all_raw_skills:
                s_uri = raw_skill.get("uri", "").strip()
                rel_type = raw_skill.get("relation_type", "essential")
                skill_obj = skill_map.get(s_uri)
                if not skill_obj:
                    continue

                if rel_type == "essential":
                    essential_count += 1
                else:
                    optional_count += 1

                existing_rel = rel_by_skill_id.get(skill_obj.id)
                if existing_rel:
                    if existing_rel.relation_type != rel_type:
                        existing_rel.relation_type = rel_type
                else:
                    new_rel = OccupationSkill(
                        occupation_id=occupation.id,
                        skill_id=skill_obj.id,
                        relation_type=rel_type,
                        created_at=utc_now()
                    )
                    db.add(new_rel)
                    rel_by_skill_id[skill_obj.id] = new_rel

            # 6. Commit single clean transaction
            db.commit()
            db.refresh(occupation)

            logger.info(
                f"Successfully ingested ESCO occupation '{occupation.title}': "
                f"{essential_count} essential, {optional_count} optional skills."
            )

            return {
                "status": "success",
                "message": f"Successfully ingested ESCO occupation '{occupation.title}'",
                "occupation": {
                    "id": occupation.id,
                    "title": occupation.title,
                    "esco_uri": occupation.esco_uri,
                    "code": occupation.code,
                    "description": occupation.description,
                    "language": occupation.language,
                    "created_at": occupation.created_at.isoformat() if occupation.created_at else None,
                    "updated_at": occupation.updated_at.isoformat() if occupation.updated_at else None,
                },
                "skills_summary": {
                    "essential_count": essential_count,
                    "optional_count": optional_count,
                    "total_count": essential_count + optional_count,
                    "sample_essential": [s["title"] for s in essential_skills_raw[:5]],
                    "sample_optional": [s["title"] for s in optional_skills_raw[:5]],
                }
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to ingest ESCO occupation '{title}': {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ingest ESCO occupation: {str(e)}"
            )

    def get_imported_occupations(
        self,
        db: Session,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all imported ESCO occupations from local PostgreSQL.
        """
        occupations = db.query(Occupation).order_by(Occupation.id.asc()).offset(offset).limit(limit).all()
        results = []
        for occ in occupations:
            essential_count = db.query(OccupationSkill).filter(
                OccupationSkill.occupation_id == occ.id,
                OccupationSkill.relation_type == "essential"
            ).count()
            optional_count = db.query(OccupationSkill).filter(
                OccupationSkill.occupation_id == occ.id,
                OccupationSkill.relation_type == "optional"
            ).count()

            results.append({
                "id": occ.id,
                "title": occ.title,
                "esco_uri": occ.esco_uri,
                "code": occ.code,
                "description": occ.description,
                "language": occ.language,
                "essential_skills_count": essential_count,
                "optional_skills_count": optional_count,
                "total_skills_count": essential_count + optional_count,
                "created_at": occ.created_at.isoformat() if occ.created_at else None,
                "updated_at": occ.updated_at.isoformat() if occ.updated_at else None,
            })
        return results

    def get_imported_occupation_details(
        self,
        db: Session,
        occupation_id: int
    ) -> Dict[str, Any]:
        """
        Retrieves details and all associated skills for an imported occupation.
        """
        occ = db.query(Occupation).filter(Occupation.id == occupation_id).first()
        if not occ:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Occupation with ID {occupation_id} not found."
            )

        relations = db.query(OccupationSkill, Skill).join(
            Skill, OccupationSkill.skill_id == Skill.id
        ).filter(OccupationSkill.occupation_id == occ.id).all()

        essential_skills = []
        optional_skills = []

        for rel, skill in relations:
            item = {
                "id": skill.id,
                "title": skill.title or skill.name,
                "name": skill.name,
                "esco_uri": skill.esco_uri,
                "skill_type": skill.skill_type,
                "category": skill.category,
                "description": skill.description,
                "relation_type": rel.relation_type
            }
            if rel.relation_type == "essential":
                essential_skills.append(item)
            else:
                optional_skills.append(item)

        return {
            "id": occ.id,
            "title": occ.title,
            "esco_uri": occ.esco_uri,
            "code": occ.code,
            "description": occ.description,
            "language": occ.language,
            "created_at": occ.created_at.isoformat() if occ.created_at else None,
            "updated_at": occ.updated_at.isoformat() if occ.updated_at else None,
            "essential_skills": essential_skills,
            "optional_skills": optional_skills,
            "essential_count": len(essential_skills),
            "optional_count": len(optional_skills),
            "total_count": len(essential_skills) + len(optional_skills)
        }


# Singleton instance
esco_ingestion_service = EscoIngestionService()
