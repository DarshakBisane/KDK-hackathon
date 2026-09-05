import json
import re
from typing import Dict, Any, List
import httpx
from fastapi import HTTPException, status
from app.config import get_settings
from app.schemas.schemas import ResumeExtraction

settings = get_settings()

RESUME_EXTRACTION_PROMPT = """
You are a specialized resume information extraction system.

Analyze the following resume text and extract structured information strictly according to these rules:
1. Extract ONLY information that is explicitly present in the resume text.
2. DO NOT invent, assume, or hallucinate any skills, experiences, or degrees.
3. DO NOT infer skills from vague statements.
4. Normalize obvious spelling and casing for skills (e.g., "ML" -> "Machine Learning", "reactjs" -> "React", "Python3" -> "Python").
5. Return ONLY a valid JSON object without any additional conversational text or explanation.

JSON Schema format required:
{
  "name": "Candidate Full Name or empty string if not found",
  "education": ["List of degrees, universities, or education entries"],
  "skills": ["List of distinct technical and soft skills explicitly mentioned"],
  "projects": ["List of project titles or summary lines"],
  "certifications": ["List of certifications"],
  "experience": ["List of work experience titles/companies"]
}

Resume Text:
\"\"\"{resume_text}\"\"\"
"""


def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """
    Extracts and parses JSON from raw model output, stripping markdown code fences if present.
    """
    if not raw_text:
        return {}

    text = raw_text.strip()
    
    # Remove markdown code block fences if any
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback regex search for outer JSON object {...}
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise ValueError("Failed to parse structured JSON from Gemini response.")


async def extract_resume_info(resume_text: str) -> ResumeExtraction:
    """
    Calls the Gemini API to extract structured resume data.
    Provides detailed error handling and fallbacks.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key.strip() == "" or "your_api_key" in api_key.lower():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API key is not configured on the backend server. Please configure GEMINI_API_KEY in .env."
        )

    # Candidate models to try in order of preference
    models_to_try = [
        settings.GEMINI_MODEL,
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]
    # Remove duplicates while preserving order
    models_to_try = list(dict.fromkeys(models_to_try))

    prompt_content = RESUME_EXTRACTION_PROMPT.replace("{resume_text}", resume_text)

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_content}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    last_error_msg = ""

    async with httpx.AsyncClient(timeout=45.0) as client:
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            try:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and len(candidates) > 0:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and len(parts) > 0:
                            raw_text = parts[0].get("text", "")
                            parsed = clean_json_response(raw_text)
                            
                            # Validate & build Pydantic schema
                            return ResumeExtraction(
                                name=parsed.get("name", "") or "",
                                education=parsed.get("education", []) if isinstance(parsed.get("education"), list) else [],
                                skills=[str(s) for s in parsed.get("skills", []) if s] if isinstance(parsed.get("skills"), list) else [],
                                projects=parsed.get("projects", []) if isinstance(parsed.get("projects"), list) else [],
                                certifications=parsed.get("certifications", []) if isinstance(parsed.get("certifications"), list) else [],
                                experience=parsed.get("experience", []) if isinstance(parsed.get("experience"), list) else []
                            )
                else:
                    error_json = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    error_msg = error_json.get("error", {}).get("message", response.text)
                    last_error_msg = f"Model {model} returned {response.status_code}: {error_msg}"
            except httpx.TimeoutException:
                last_error_msg = f"Timeout connecting to Gemini model {model}"
            except Exception as e:
                last_error_msg = str(e)

    # If all models failed
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Unable to analyze the resume with Gemini AI right now. Please try again. ({last_error_msg[:120]})"
    )
