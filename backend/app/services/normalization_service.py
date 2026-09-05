import re
from typing import List, Set, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import Skill, SkillAlias, utc_now


# Standard canonical aliases mapping
SKILL_ALIASES = {
    # AI / ML / Data
    "ml": "Machine Learning",
    "machine-learning": "Machine Learning",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "mlflow": "MLflow",
    "ml flow": "MLflow",
    "model monitoring": "Model Monitoring",
    "model-monitoring": "Model Monitoring",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "tableau": "Tableau",
    "data visualization": "Data Visualization",
    "data-viz": "Data Visualization",
    "dataviz": "Data Visualization",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "statistics": "Statistics",
    "excel": "Excel",
    "ms excel": "Excel",
    "dbt": "dbt",

    # Frontend
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react js": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",

    # Backend
    "python": "Python",
    "python3": "Python",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "rest api": "REST API",
    "rest": "REST API",
    "restful api": "REST API",
    "graphql": "GraphQL",

    # Databases & Cloud / DevOps
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "git": "Git",
    "github": "Git",
    "gitlab": "Git",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "linux": "Linux",
    "cybersecurity": "Cybersecurity",
    "network security": "Network Security",
    "ethical hacking": "Ethical Hacking",
}


def normalize_skill_name(raw_name: str) -> str:
    """
    Normalizes a single skill string:
    - strips whitespace
    - matches against known alias table (case-insensitive)
    - defaults to title-cased representation
    """
    if not raw_name:
        return ""

    cleaned = raw_name.strip()
    lookup_key = re.sub(r"\s+", " ", cleaned.lower())

    if lookup_key in SKILL_ALIASES:
        return SKILL_ALIASES[lookup_key]

    # Clean punctuation if edge case
    lookup_key_clean = lookup_key.replace("-", " ").replace(".", "")
    if lookup_key_clean in SKILL_ALIASES:
        return SKILL_ALIASES[lookup_key_clean]

    return cleaned.title()


def normalize_skills_list(skills: List[str]) -> List[str]:
    """
    Normalizes a list of skills, deduplicating while preserving order.
    """
    seen: Set[str] = set()
    normalized: List[str] = []

    for s in skills:
        if not s or not isinstance(s, str):
            continue
        norm = normalize_skill_name(s)
        if norm and norm.lower() not in seen:
            seen.add(norm.lower())
            normalized.append(norm)

    return normalized


def get_or_create_canonical_skill(
    db: Session,
    raw_name: str,
    category: str = "General"
) -> Tuple[Skill, bool, Optional[SkillAlias]]:
    """
    Looks up or creates a canonical Skill in PostgreSQL:
    1. Checks dictionary normalization
    2. Checks DB SkillAlias table
    3. Checks DB Skill table
    4. Creates canonical Skill if brand new, and registers alias if distinct.
    Returns: (skill_instance, was_created, created_alias)
    """
    if not raw_name or not raw_name.strip():
        raise ValueError("Skill name cannot be empty.")

    cleaned_raw = raw_name.strip()
    norm_name = normalize_skill_name(cleaned_raw)

    # 1. Check SkillAlias table in DB
    existing_alias = db.query(SkillAlias).filter(
        func.lower(SkillAlias.alias) == cleaned_raw.lower()
    ).first()

    if existing_alias:
        skill = db.query(Skill).filter(Skill.id == existing_alias.skill_id).first()
        if skill:
            return skill, False, None

    # 2. Check canonical Skill table
    skill = db.query(Skill).filter(
        (func.lower(Skill.name) == norm_name.lower()) | (func.lower(Skill.name) == cleaned_raw.lower())
    ).first()

    if skill:
        created_alias = None
        # Record raw_name as an alias if distinct and not already recorded
        if cleaned_raw.lower() != skill.name.lower():
            alias_exists = db.query(SkillAlias).filter(
                func.lower(SkillAlias.alias) == cleaned_raw.lower()
            ).first()
            if not alias_exists:
                created_alias = SkillAlias(
                    skill_id=skill.id,
                    alias=cleaned_raw,
                    source="normalization_auto"
                )
                db.add(created_alias)
                db.flush()
        return skill, False, created_alias

    # 3. Create new canonical Skill
    new_skill = Skill(
        name=norm_name,
        category=category,
        first_detected_at=utc_now(),
        last_updated_at=utc_now(),
        created_at=utc_now(),
        updated_at=utc_now()
    )
    db.add(new_skill)
    db.flush()

    created_alias = None
    if cleaned_raw.lower() != norm_name.lower():
        created_alias = SkillAlias(
            skill_id=new_skill.id,
            alias=cleaned_raw,
            source="normalization_auto"
        )
        db.add(created_alias)
        db.flush()

    return new_skill, True, created_alias
