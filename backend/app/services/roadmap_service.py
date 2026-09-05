from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import User, Skill, RoadmapItem
from app.services.skill_gap_service import calculate_skill_gap


# Deterministic topic blueprints for common skills
SKILL_ROADMAP_BLUEPRINTS: Dict[str, Dict[str, str]] = {
    "Machine Learning": {
        "title": "Machine Learning Fundamentals & Algorithms",
        "description": "Master supervised vs unsupervised learning, regression, classification, cross-validation, and loss functions."
    },
    "Scikit-learn": {
        "title": "Model Building & Pipelines with Scikit-learn",
        "description": "Implement end-to-end data preprocessing pipelines, hyperparameter tuning via GridSearchCV, and model evaluation metrics."
    },
    "Deep Learning": {
        "title": "Neural Networks & Deep Learning Architectures",
        "description": "Understand multi-layer perceptrons, backpropagation, CNNs/RNNs, and activation functions for deep feature extraction."
    },
    "PyTorch": {
        "title": "Deep Learning with PyTorch",
        "description": "Build tensors, autograd computation graphs, custom PyTorch nn.Module layers, and training loops with GPU acceleration."
    },
    "Docker": {
        "title": "Containerization & Deployment with Docker",
        "description": "Write efficient multi-stage Dockerfiles, manage images, compose multi-container services, and deploy isolated environments."
    },
    "Kubernetes": {
        "title": "Orchestration & Scaling with Kubernetes",
        "description": "Deploy pods, services, ingress controllers, and config maps for high-availability production workloads."
    },
    "FastAPI": {
        "title": "Modern Asynchronous APIs with FastAPI",
        "description": "Build fast, type-safe REST APIs using Pydantic schemas, dependency injection, and automatic OpenAPI documentation."
    },
    "SQL": {
        "title": "Advanced SQL & Database Modeling",
        "description": "Write complex multi-table joins, subqueries, CTEs, indexing strategies, and query performance optimizations."
    },
    "PostgreSQL": {
        "title": "Relational Data Management with PostgreSQL",
        "description": "Design normalized schemas, foreign keys, transaction ACID isolation levels, and full-text search indexing."
    },
    "React": {
        "title": "Interactive Modern UIs with React",
        "description": "Master functional components, custom hooks, state management, memoization, and component composition."
    },
    "TypeScript": {
        "title": "Type-Safe Web Applications with TypeScript",
        "description": "Implement interfaces, generics, union types, and strict compilation checks across frontend applications."
    },
    "Power BI": {
        "title": "Interactive Dashboarding with Power BI",
        "description": "Build data models, DAX measures, automated ETL transformations, and executive business intelligence reports."
    },
    "Data Visualization": {
        "title": "Visual Data Storytelling",
        "description": "Design intuitive visual representations of complex numerical datasets using modern charts, palettes, and layouts."
    },
    "Statistics": {
        "title": "Applied Statistical Inference & Probability",
        "description": "Apply hypothesis testing, p-values, confidence intervals, A/B test analysis, and probability distributions."
    },
    "CI/CD": {
        "title": "Automated CI/CD Deployment Pipelines",
        "description": "Configure GitHub Actions workflows for automated testing, linting, security scans, and production deployments."
    },
    "AWS": {
        "title": "Cloud Architecture & Core AWS Services",
        "description": "Deploy and configure compute (EC2), storage (S3), serverless (Lambda), and networking (VPC, IAM security)."
    },
    "Linux": {
        "title": "Linux System Administration & Shell Scripting",
        "description": "Master bash scripting, process management, file permissions, systemd services, and remote server access."
    },
    "Cybersecurity": {
        "title": "Core Security Principles & Threat Defense",
        "description": "Understand OWASP top 10 vulnerabilities, authentication vulnerabilities, encryption, and secure coding practices."
    },
    "Network Security": {
        "title": "Network Protocols & Traffic Analysis",
        "description": "Inspect TCP/IP packet flows, configure firewalls, TLS/SSL certificates, and identify suspicious network behaviors."
    },
    "Natural Language Processing": {
        "title": "NLP & Language Model Applications",
        "description": "Implement text embeddings, tokenization, transformer architectures, and semantic search interfaces."
    },
}


def generate_or_get_roadmap(user_id: int, db: Session) -> List[RoadmapItem]:
    """
    Retrieves the student's roadmap items.
    If none exist or if new missing skills emerged, generates roadmap items
    deterministically from the target career's missing skills.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    existing_items = (
        db.query(RoadmapItem)
        .filter(RoadmapItem.user_id == user_id)
        .order_by(RoadmapItem.week.asc())
        .all()
    )

    gap_data = calculate_skill_gap(user_id, db)
    missing_skills = gap_data.missing_skills

    if not missing_skills:
        # If user has no missing skills or already achieved 100%
        return existing_items

    # Check if roadmap already aligns with current missing skills
    existing_skills_in_roadmap = {item.skill.name.lower() for item in existing_items if item.skill}
    current_missing_names = {s["name"].lower() for s in missing_skills}

    # If existing roadmap matches current missing skills, return them
    if existing_items and existing_skills_in_roadmap == current_missing_names:
        return existing_items

    # Otherwise, rebuild roadmap to precisely match current missing skills while preserving completed status if any
    status_map = {item.skill.name.lower(): item.status for item in existing_items if item.skill}
    
    # Delete old items
    db.query(RoadmapItem).filter(RoadmapItem.user_id == user_id).delete()
    db.flush()

    new_items = []
    for index, skill_entry in enumerate(missing_skills, start=1):
        skill_name = skill_entry["name"]
        importance = skill_entry["importance"]
        skill_obj = db.query(Skill).filter(Skill.name == skill_name).first()

        blueprint = SKILL_ROADMAP_BLUEPRINTS.get(
            skill_name,
            {
                "title": f"Master {skill_name} Fundamentals",
                "description": f"Learn core principles, syntax, real-world patterns, and hands-on practice projects for {skill_name}."
            }
        )

        prev_status = status_map.get(skill_name.lower(), "Not Started")

        item = RoadmapItem(
            user_id=user_id,
            skill_id=skill_obj.id if skill_obj else None,
            title=blueprint["title"],
            description=blueprint["description"],
            week=index,
            status=prev_status,
            importance=importance
        )
        db.add(item)
        new_items.append(item)

    db.commit()
    for item in new_items:
        db.refresh(item)

    return new_items


def update_roadmap_item_status(user_id: int, item_id: int, new_status: str, db: Session) -> Optional[RoadmapItem]:
    """
    Updates the learning progress status of a roadmap item.
    """
    item = db.query(RoadmapItem).filter(
        RoadmapItem.id == item_id,
        RoadmapItem.user_id == user_id
    ).first()

    if not item:
        return None

    item.status = new_status
    db.commit()
    db.refresh(item)
    return item
