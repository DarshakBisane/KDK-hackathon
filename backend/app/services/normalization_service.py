import re
from typing import List, Set


# Standard canonical aliases mapping (Phase 1 seed normalization)
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

    # Frontend
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
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
    - defaults to title-cased or canonical representation
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

    # Return capitalised format
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
