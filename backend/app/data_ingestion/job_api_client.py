import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import httpx

from app.config import get_settings

logger = logging.getLogger("skillgap.job_api")
settings = get_settings()


class JobPosting(BaseModel):
    title: str
    company: str = "Industry Tech Corp"
    description: str
    url: str = "https://example.com/jobs/posting"
    source: str = "job_api"
    explicit_skills: List[str] = Field(default_factory=list)


# Realistic curated mock job market dataset for demonstration & robust offline fallback
MOCK_CAREER_JOBS: Dict[str, List[Dict[str, Any]]] = {
    "ML Engineer": [
        {
            "title": "Machine Learning Engineer - Model Pipelines",
            "company": "DeepScale AI",
            "description": "We are seeking a Machine Learning Engineer with strong Python and Scikit-learn expertise. You will package machine learning pipelines with Docker and manage experiment tracking using MLflow.",
            "url": "https://jobs.example.com/ml-engineer-1",
            "source": "job_api",
            "explicit_skills": ["Python", "Machine Learning", "Scikit-learn", "Docker", "MLflow"]
        },
        {
            "title": "Senior ML Engineer - Production Systems",
            "company": "NeuralTech Global",
            "description": "Build high-throughput prediction services. Requirements: Python, SQL, Docker, MLflow for model registry, Kubernetes for deployment, and solid machine learning foundations.",
            "url": "https://jobs.example.com/ml-engineer-2",
            "source": "job_api",
            "explicit_skills": ["Python", "Machine Learning", "SQL", "Docker", "MLflow", "Kubernetes"]
        },
        {
            "title": "ML Platform & Infrastructure Engineer",
            "company": "CloudData Labs",
            "description": "Join our ML platform team. Deep learning model optimization, Docker containers, Kubernetes orchestration, MLflow lifecycle management, and Python development.",
            "url": "https://jobs.example.com/ml-engineer-3",
            "source": "job_api",
            "explicit_skills": ["Python", "Deep Learning", "Docker", "MLflow", "Kubernetes"]
        },
        {
            "title": "Applied Machine Learning Engineer",
            "company": "Visionary AI Systems",
            "description": "Deploying machine learning models using FastAPI microservices and Docker. Must have hands-on experience tracking runs in MLflow, using Git for version control, and Python.",
            "url": "https://jobs.example.com/ml-engineer-4",
            "source": "job_api",
            "explicit_skills": ["Python", "Machine Learning", "FastAPI", "Docker", "MLflow", "Git"]
        },
        {
            "title": "MLOps / Machine Learning Specialist",
            "company": "NextGen Dynamics",
            "description": "Lead our MLOps initiative. Build continuous training pipelines with MLflow, Model Monitoring, Scikit-learn, Docker, Python, and Machine Learning workflows.",
            "url": "https://jobs.example.com/ml-engineer-5",
            "source": "job_api",
            "explicit_skills": ["Python", "Machine Learning", "MLflow", "Model Monitoring", "Docker", "Scikit-learn"]
        }
    ],
    "Data Analyst": [
        {
            "title": "Senior Data Analyst - Business Insights",
            "company": "FinMetrics Corp",
            "description": "Transform data using SQL, Excel, Power BI dashboards, Python data preparation, and dbt for data transformations.",
            "url": "https://jobs.example.com/data-analyst-1",
            "source": "job_api",
            "explicit_skills": ["SQL", "Excel", "Power BI", "Python", "Data Visualization", "dbt"]
        },
        {
            "title": "BI & Analytics Specialist",
            "company": "Retail Insights",
            "description": "Building interactive Power BI reports, complex SQL queries, statistical analysis, and automated Python data feeds.",
            "url": "https://jobs.example.com/data-analyst-2",
            "source": "job_api",
            "explicit_skills": ["SQL", "Power BI", "Statistics", "Python", "Tableau", "Data Visualization"]
        }
    ],
    "Backend Developer": [
        {
            "title": "Backend Software Engineer",
            "company": "Scalable Services Inc",
            "description": "Building high-performance REST APIs with Python and FastAPI. PostgreSQL database design, Docker containerization, and Redis caching.",
            "url": "https://jobs.example.com/backend-dev-1",
            "source": "job_api",
            "explicit_skills": ["Python", "FastAPI", "PostgreSQL", "REST API", "Docker", "Redis"]
        },
        {
            "title": "Senior Backend API Developer",
            "company": "CloudPeak Technologies",
            "description": "Architecting resilient microservices with Python, FastAPI, SQL, Git workflows, Docker, and Kafka event streaming.",
            "url": "https://jobs.example.com/backend-dev-2",
            "source": "job_api",
            "explicit_skills": ["Python", "FastAPI", "SQL", "Git", "Docker", "REST API", "PostgreSQL"]
        }
    ],
    "Frontend Developer": [
        {
            "title": "Frontend React Engineer",
            "company": "PixelCraft UI",
            "description": "Crafting responsive web applications with React, TypeScript, modern CSS, Tailwind CSS, and REST API integrations.",
            "url": "https://jobs.example.com/frontend-dev-1",
            "source": "job_api",
            "explicit_skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Tailwind CSS", "REST API"]
        }
    ]
}


class MockJobDataProvider:
    """
    Provides realistic job market postings for careers in development, testing,
    and demo modes without requiring external network access.
    """

    @classmethod
    def get_jobs_for_career(cls, career_name: str, limit: int = 5) -> List[JobPosting]:
        # Search by exact or partial match
        matched_jobs_data = MOCK_CAREER_JOBS.get(career_name)

        if not matched_jobs_data:
            # Fallback search by substring
            for key, jobs in MOCK_CAREER_JOBS.items():
                if key.lower() in career_name.lower() or career_name.lower() in key.lower():
                    matched_jobs_data = jobs
                    break

        if not matched_jobs_data:
            # Default generic tech postings if unknown career
            matched_jobs_data = [
                {
                    "title": f"Senior {career_name} Specialist",
                    "company": "Global Tech Ventures",
                    "description": f"Exciting opportunity for a {career_name}. Strong foundations in Python, Git, and REST API required.",
                    "url": "https://jobs.example.com/generic-1",
                    "source": "mock_provider",
                    "explicit_skills": ["Python", "Git", "REST API", "SQL"]
                }
            ]

        postings = [JobPosting(**item) for item in matched_jobs_data[:limit]]
        return postings


class JobApiClient:
    """
    Client for retrieving live job market postings from external Job APIs (e.g. Adzuna, Reed, etc.)
    with automatic and resilient fallback to the mock provider.
    """

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = (api_url or settings.JOB_API_URL).strip()
        self.api_key = (api_key or settings.JOB_API_KEY).strip()

    def is_external_configured(self) -> bool:
        return bool(
            self.api_url
            and self.api_key
            and not self.api_key.startswith("your_")
            and not self.api_url.startswith("your_")
        )

    async def get_jobs_for_career_async(self, career_name: str, limit: int = 5) -> List[JobPosting]:
        if not self.is_external_configured():
            logger.info(f"External Job API not configured. Using high-fidelity MockJobDataProvider for '{career_name}'.")
            return MockJobDataProvider.get_jobs_for_career(career_name, limit=limit)

        try:
            logger.info(f"Fetching live job postings for '{career_name}' from external Job API: {self.api_url}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "what": career_name,
                    "results_per_page": limit,
                    "content-type": "application/json"
                }
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.get(self.api_url, params=params, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", []) or data.get("jobs", [])
                    if results:
                        postings: List[JobPosting] = []
                        for item in results[:limit]:
                            postings.append(JobPosting(
                                title=item.get("title", f"{career_name} Role"),
                                company=item.get("company", {}).get("display_name", "Industry Employer") if isinstance(item.get("company"), dict) else str(item.get("company", "Industry Employer")),
                                description=item.get("description", ""),
                                url=item.get("redirect_url", item.get("url", "https://example.com/job")),
                                source="external_job_api",
                                explicit_skills=item.get("skills", []) if isinstance(item.get("skills"), list) else []
                            ))
                        return postings

                logger.warning(f"External Job API returned status {response.status_code}. Falling back to mock provider.")
        except Exception as e:
            logger.warning(f"Failed to query external Job API ({e}). Falling back to mock provider.")

        return MockJobDataProvider.get_jobs_for_career(career_name, limit=limit)

    def get_jobs_for_career(self, career_name: str, limit: int = 5) -> List[JobPosting]:
        """Synchronous wrapper for job retrieval."""
        if not self.is_external_configured():
            return MockJobDataProvider.get_jobs_for_career(career_name, limit=limit)

        try:
            with httpx.Client(timeout=10.0) as client:
                params = {
                    "what": career_name,
                    "results_per_page": limit,
                    "content-type": "application/json"
                }
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = client.get(self.api_url, params=params, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", []) or data.get("jobs", [])
                    if results:
                        postings: List[JobPosting] = []
                        for item in results[:limit]:
                            postings.append(JobPosting(
                                title=item.get("title", f"{career_name} Role"),
                                company=item.get("company", {}).get("display_name", "Industry Employer") if isinstance(item.get("company"), dict) else str(item.get("company", "Industry Employer")),
                                description=item.get("description", ""),
                                url=item.get("redirect_url", item.get("url", "https://example.com/job")),
                                source="external_job_api",
                                explicit_skills=item.get("skills", []) if isinstance(item.get("skills"), list) else []
                            ))
                        return postings
        except Exception as e:
            logger.warning(f"Sync external job fetch error ({e}). Using mock provider.")

        return MockJobDataProvider.get_jobs_for_career(career_name, limit=limit)
