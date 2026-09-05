import logging
from typing import Dict, Any, List, Optional
import httpx
from fastapi import HTTPException, status

from app.config import get_settings

logger = logging.getLogger("skillgap.esco")
settings = get_settings()


def extract_esco_description(raw_desc: Any, language: str = "en") -> str:
    """Extracts plain text description from ESCO multilingual description object."""
    if not raw_desc:
        return ""
    if isinstance(raw_desc, dict):
        lang_dict = raw_desc.get(language) or raw_desc.get("en")
        if isinstance(lang_dict, dict):
            return lang_dict.get("literal", "") or lang_dict.get("value", "") or str(lang_dict)
        elif isinstance(lang_dict, str):
            return lang_dict
        return raw_desc.get("literal", "") or str(raw_desc)
    return str(raw_desc).strip()


def clean_esco_skill_type(raw_type: Optional[str]) -> str:
    """Extracts short skill type (e.g. 'skill', 'knowledge') from ESCO URI or string."""
    if not raw_type:
        return "skill"
    raw_str = str(raw_type).strip()
    if "/" in raw_str:
        return raw_str.rstrip("/").split("/")[-1]
    return raw_str


class EscoClient:
    """
    Client for the official European Commission ESCO Web Service API.
    Provides methods to search occupations, retrieve occupational details,
    and fetch essential & optional skills.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.ESCO_API_BASE_URL).rstrip("/")

    async def search_occupations_async(
        self,
        query: str,
        limit: int = 10,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Searches occupations in the official European Commission ESCO API.
        Endpoint: GET https://ec.europa.eu/esco/api/search
        Params: text, type=occupation, language, limit
        """
        if not query or not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query 'q' cannot be empty."
            )

        url = f"{self.base_url}/search"
        params = {
            "text": query.strip(),
            "type": "occupation",
            "language": language,
            "limit": limit
        }

        logger.info(f"Calling official ESCO search API: {url} with params {params}")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("_embedded", {}).get("results", [])
                    
                    occupations = []
                    for item in results:
                        occupations.append({
                            "title": item.get("title", ""),
                            "uri": item.get("uri", ""),
                            "code": item.get("code", ""),
                            "description": extract_esco_description(item.get("description"), language=language)
                        })

                    return {
                        "query": query.strip(),
                        "language": language,
                        "total_results": data.get("total", len(occupations)),
                        "returned_results": len(occupations),
                        "occupations": occupations,
                        "esco_api_source": "Official European Commission ESCO Web Service"
                    }
                else:
                    logger.error(f"ESCO API returned HTTP {response.status_code}: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Official ESCO Web Service returned HTTP {response.status_code}."
                    )
        except httpx.TimeoutException:
            logger.error(f"Timeout while connecting to official ESCO API at {url}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to official European Commission ESCO API timed out. Please try again."
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error querying official ESCO API: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while connecting to official ESCO API: {str(e)}"
            )

    def search_occupations(
        self,
        query: str,
        limit: int = 10,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Synchronous search method for occupations.
        """
        if not query or not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query 'q' cannot be empty."
            )

        url = f"{self.base_url}/search"
        params = {
            "text": query.strip(),
            "type": "occupation",
            "language": language,
            "limit": limit
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("_embedded", {}).get("results", [])
                    occupations = []
                    for item in results:
                        occupations.append({
                            "title": item.get("title", ""),
                            "uri": item.get("uri", ""),
                            "code": item.get("code", ""),
                            "description": extract_esco_description(item.get("description"), language=language)
                        })

                    return {
                        "query": query.strip(),
                        "language": language,
                        "total_results": data.get("total", len(occupations)),
                        "returned_results": len(occupations),
                        "occupations": occupations,
                        "esco_api_source": "Official European Commission ESCO Web Service"
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Official ESCO Web Service returned HTTP {response.status_code}."
                    )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to official European Commission ESCO API timed out."
            )

    async def get_occupation_details_async(
        self,
        uri: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Fetches full occupation details including essential and optional skills.
        Endpoint: GET https://ec.europa.eu/esco/api/resource/occupation
        Params: uri, language
        """
        if not uri or not uri.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ESCO occupation URI cannot be empty."
            )

        url = f"{self.base_url}/resource/occupation"
        params = {
            "uri": uri.strip(),
            "language": language
        }

        logger.info(f"Calling official ESCO occupation resource API: {url} for URI: {uri}")

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_occupation_resource(data, language=language)
                elif response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"ESCO occupation with URI '{uri}' was not found."
                    )
                else:
                    logger.error(f"ESCO API returned HTTP {response.status_code}: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Official ESCO Web Service returned HTTP {response.status_code}."
                    )
        except httpx.TimeoutException:
            logger.error(f"Timeout while fetching occupation from ESCO API at {url}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to official European Commission ESCO API timed out."
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching occupation details: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error connecting to official ESCO API: {str(e)}"
            )

    def get_occupation_details(
        self,
        uri: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Synchronous method to fetch full occupation details and skills.
        """
        if not uri or not uri.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ESCO occupation URI cannot be empty."
            )

        url = f"{self.base_url}/resource/occupation"
        params = {
            "uri": uri.strip(),
            "language": language
        }

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_occupation_resource(data, language=language)
                elif response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"ESCO occupation with URI '{uri}' was not found."
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Official ESCO Web Service returned HTTP {response.status_code}."
                    )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to official European Commission ESCO API timed out."
            )

    def _parse_occupation_resource(self, data: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """Parses the raw JSON from ESCO occupation resource endpoint."""
        links = data.get("_links", {})
        essential_links = links.get("hasEssentialSkill", [])
        optional_links = links.get("hasOptionalSkill", [])

        essential_skills = []
        for s in essential_links:
            essential_skills.append({
                "uri": s.get("uri", ""),
                "title": s.get("title", ""),
                "skill_type": clean_esco_skill_type(s.get("skillType")),
                "relation_type": "essential"
            })

        optional_skills = []
        for s in optional_links:
            optional_skills.append({
                "uri": s.get("uri", ""),
                "title": s.get("title", ""),
                "skill_type": clean_esco_skill_type(s.get("skillType")),
                "relation_type": "optional"
            })

        return {
            "uri": data.get("uri", ""),
            "title": data.get("title", "") or (data.get("preferredLabel", {}).get(language, "") if isinstance(data.get("preferredLabel"), dict) else str(data.get("preferredLabel") or "")),
            "code": data.get("code", "") or (data.get("codes", [None])[0] if isinstance(data.get("codes"), list) and data.get("codes") else None),
            "description": extract_esco_description(data.get("description"), language=language),
            "language": language,
            "essential_skills": essential_skills,
            "optional_skills": optional_skills,
            "essential_count": len(essential_skills),
            "optional_count": len(optional_skills),
            "total_skills_count": len(essential_skills) + len(optional_skills)
        }

    async def get_skill_details_async(
        self,
        uri: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Fetches full skill details from the official ESCO API.
        Endpoint: GET https://ec.europa.eu/esco/api/resource/skill
        Params: uri, language
        """
        if not uri or not uri.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ESCO skill URI cannot be empty."
            )

        url = f"{self.base_url}/resource/skill"
        params = {"uri": uri.strip(), "language": language}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "uri": data.get("uri", ""),
                        "title": data.get("title", ""),
                        "description": extract_esco_description(data.get("description"), language=language),
                        "skill_type": clean_esco_skill_type(data.get("skillType")),
                        "language": language
                    }
                elif response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"ESCO skill with URI '{uri}' was not found."
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Official ESCO Web Service returned HTTP {response.status_code}."
                    )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to official European Commission ESCO API timed out."
            )


# Singleton instance
esco_client = EscoClient()
