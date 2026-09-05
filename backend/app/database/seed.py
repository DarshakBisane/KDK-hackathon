from sqlalchemy.orm import Session
from app.models.models import Career, Skill, CareerSkill


INITIAL_CAREERS = [
    {
        "name": "ML Engineer",
        "description": "Designs, builds, and deploys scalable machine learning and deep learning models into production pipelines.",
        "icon": "Brain",
        "category": "AI / Machine Learning",
        "skills": [
            ("Python", "HIGH"),
            ("Machine Learning", "HIGH"),
            ("Scikit-learn", "HIGH"),
            ("Deep Learning", "HIGH"),
            ("SQL", "HIGH"),
            ("NumPy", "MEDIUM"),
            ("Pandas", "MEDIUM"),
            ("Docker", "MEDIUM"),
        ]
    },
    {
        "name": "Data Analyst",
        "description": "Transforms raw business data into actionable visual insights, interactive dashboards, and strategic reports.",
        "icon": "BarChart3",
        "category": "Data & Business Intelligence",
        "skills": [
            ("SQL", "HIGH"),
            ("Excel", "HIGH"),
            ("Power BI", "HIGH"),
            ("Python", "HIGH"),
            ("Data Visualization", "HIGH"),
            ("Pandas", "MEDIUM"),
            ("Statistics", "MEDIUM"),
        ]
    },
    {
        "name": "Data Scientist",
        "description": "Applies statistical modeling, machine learning algorithms, and exploratory data analysis to solve complex problems.",
        "icon": "LineChart",
        "category": "Data Science",
        "skills": [
            ("Python", "HIGH"),
            ("SQL", "HIGH"),
            ("Statistics", "HIGH"),
            ("Machine Learning", "HIGH"),
            ("Pandas", "HIGH"),
            ("NumPy", "MEDIUM"),
            ("Scikit-learn", "MEDIUM"),
            ("Data Visualization", "MEDIUM"),
        ]
    },
    {
        "name": "AI Engineer",
        "description": "Develops generative AI applications, neural network architectures, LLM integrations, and intelligent agent systems.",
        "icon": "Sparkles",
        "category": "Artificial Intelligence",
        "skills": [
            ("Python", "HIGH"),
            ("Deep Learning", "HIGH"),
            ("Machine Learning", "HIGH"),
            ("PyTorch", "HIGH"),
            ("REST API", "HIGH"),
            ("Docker", "MEDIUM"),
            ("Git", "MEDIUM"),
            ("Natural Language Processing", "MEDIUM"),
        ]
    },
    {
        "name": "Backend Developer",
        "description": "Architects resilient server-side applications, high-throughput REST APIs, database schemas, and background services.",
        "icon": "Server",
        "category": "Software Engineering",
        "skills": [
            ("Python", "HIGH"),
            ("FastAPI", "HIGH"),
            ("SQL", "HIGH"),
            ("REST API", "HIGH"),
            ("Git", "MEDIUM"),
            ("Docker", "MEDIUM"),
            ("PostgreSQL", "MEDIUM"),
        ]
    },
    {
        "name": "Frontend Developer",
        "description": "Crafts responsive, accessible, and high-performance client-side web user interfaces and interactive web apps.",
        "icon": "Layout",
        "category": "Web Development",
        "skills": [
            ("HTML", "HIGH"),
            ("CSS", "HIGH"),
            ("JavaScript", "HIGH"),
            ("React", "HIGH"),
            ("TypeScript", "MEDIUM"),
            ("Git", "MEDIUM"),
            ("REST API", "MEDIUM"),
        ]
    },
    {
        "name": "Full Stack Developer",
        "description": "Bridges frontend user experiences with backend services, database management, and end-to-end web deployment.",
        "icon": "Layers",
        "category": "Software Engineering",
        "skills": [
            ("React", "HIGH"),
            ("Node.js", "HIGH"),
            ("Python", "HIGH"),
            ("SQL", "HIGH"),
            ("REST API", "HIGH"),
            ("HTML", "MEDIUM"),
            ("CSS", "MEDIUM"),
            ("Git", "MEDIUM"),
            ("Docker", "MEDIUM"),
        ]
    },
    {
        "name": "Cloud Engineer",
        "description": "Designs, implements, and maintains scalable multi-tenant infrastructure and cloud services on AWS/GCP/Azure.",
        "icon": "Cloud",
        "category": "Cloud & Infrastructure",
        "skills": [
            ("AWS", "HIGH"),
            ("Linux", "HIGH"),
            ("Docker", "HIGH"),
            ("Kubernetes", "HIGH"),
            ("Python", "MEDIUM"),
            ("Git", "MEDIUM"),
            ("CI/CD", "MEDIUM"),
        ]
    },
    {
        "name": "DevOps Engineer",
        "description": "Automates continuous integration and delivery pipelines, container orchestration, monitoring, and infrastructure as code.",
        "icon": "Cpu",
        "category": "DevOps & SRE",
        "skills": [
            ("Docker", "HIGH"),
            ("Kubernetes", "HIGH"),
            ("CI/CD", "HIGH"),
            ("Linux", "HIGH"),
            ("AWS", "MEDIUM"),
            ("Git", "MEDIUM"),
            ("Python", "MEDIUM"),
        ]
    },
    {
        "name": "Cybersecurity Analyst",
        "description": "Protects networks, applications, and corporate infrastructure against security vulnerabilities, malware, and intrusions.",
        "icon": "ShieldCheck",
        "category": "Security",
        "skills": [
            ("Cybersecurity", "HIGH"),
            ("Network Security", "HIGH"),
            ("Linux", "HIGH"),
            ("Python", "HIGH"),
            ("SQL", "MEDIUM"),
            ("Git", "MEDIUM"),
        ]
    },
]


def seed_database(db: Session):
    """
    Seeds initial careers and skills if not already present.
    """
    # Check if careers already seeded
    existing_careers_count = db.query(Career).count()
    if existing_careers_count > 0:
        return

    # Cache skills to avoid duplicates
    skill_cache = {}

    for career_info in INITIAL_CAREERS:
        career = Career(
            name=career_info["name"],
            description=career_info["description"],
            icon=career_info["icon"],
            category=career_info["category"]
        )
        db.add(career)
        db.flush()  # To populate career.id

        for skill_name, importance in career_info["skills"]:
            if skill_name not in skill_cache:
                skill = db.query(Skill).filter(Skill.name == skill_name).first()
                if not skill:
                    skill = Skill(name=skill_name, category=career_info["category"])
                    db.add(skill)
                    db.flush()
                skill_cache[skill_name] = skill
            else:
                skill = skill_cache[skill_name]

            # Create CareerSkill link
            career_skill = CareerSkill(
                career_id=career.id,
                skill_id=skill.id,
                importance=importance
            )
            db.add(career_skill)

    db.commit()
