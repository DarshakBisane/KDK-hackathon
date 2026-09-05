from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.esco_service import esco_client
from app.services.esco_ingestion_service import esco_ingestion_service

router = APIRouter(prefix="/esco", tags=["European Commission ESCO Web Service"])


class IngestOccupationRequest(BaseModel):
    query: Optional[str] = Field(None, description="Occupation search term (e.g. 'software developer')")
    uri: Optional[str] = Field(None, description="Direct ESCO occupation URI")
    language: str = Field("en", description="Language code (default: 'en')")


@router.get("/occupations/search")
async def search_esco_occupations(
    q: str = Query(..., min_length=1, description="Occupation search term, e.g. 'software developer'"),
    limit: int = Query(10, ge=1, le=50, description="Max number of occupational results to return"),
    language: str = Query("en", description="Language code (e.g. 'en')")
) -> Dict[str, Any]:
    """
    Searches official European Commission ESCO occupations.
    Directly queries: https://ec.europa.eu/esco/api/search?type=occupation
    """
    return await esco_client.search_occupations_async(query=q, limit=limit, language=language)


@router.get("/occupations/details")
async def get_esco_occupation_details(
    uri: str = Query(..., min_length=5, description="Full ESCO occupation URI"),
    language: str = Query("en", description="Language code (e.g. 'en')")
) -> Dict[str, Any]:
    """
    Fetches complete occupation resource details from official ESCO API.
    Directly queries: https://ec.europa.eu/esco/api/resource/occupation
    """
    return await esco_client.get_occupation_details_async(uri=uri, language=language)


@router.post("/occupations/ingest")
async def ingest_esco_occupation(
    payload: IngestOccupationRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Ingests an ESCO occupation and its essential/optional skills into PostgreSQL.
    Can accept either a search query or a direct ESCO occupation URI.
    """
    if payload.uri:
        return await esco_ingestion_service.ingest_occupation_by_uri_async(
            db=db,
            esco_uri=payload.uri,
            language=payload.language
        )
    elif payload.query:
        return await esco_ingestion_service.ingest_occupation_by_search_async(
            db=db,
            query=payload.query,
            language=payload.language
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'query' or 'uri' must be provided in request body."
        )


@router.get("/occupations/stored")
def get_stored_occupations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Lists all ESCO occupations currently imported into the local PostgreSQL database.
    """
    return esco_ingestion_service.get_imported_occupations(db=db, limit=limit, offset=offset)


@router.get("/occupations/stored/{occupation_id}")
def get_stored_occupation_details(
    occupation_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Gets details and all associated skills for a specific imported occupation.
    """
    return esco_ingestion_service.get_imported_occupation_details(db=db, occupation_id=occupation_id)
