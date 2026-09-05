import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.database.seed import seed_database
from app.main import app
from app.models.models import (
    User,
    Career,
    Skill,
    SkillAlias,
    SkillEvidence,
    CareerSkill,
    StudentSkill,
    Occupation,
    OccupationSkill
)
from app.services.normalization_service import (
    normalize_skill_name,
    get_or_create_canonical_skill
)
from app.services.skill_intelligence_service import process_career_job_postings
from app.data_ingestion.job_api_client import JobPosting, MockJobDataProvider

# In-memory SQLite database for fast isolated unit tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ==========================================
# PHASE 1 TESTS (PRESERVED FUNCTIONALITY)
# ==========================================

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_careers_seed(client):
    response = client.get("/api/careers")
    assert response.status_code == 200
    careers = response.json()
    assert len(careers) >= 10
    names = [c["name"] for c in careers]
    assert "ML Engineer" in names
    assert "Data Analyst" in names
    assert "Backend Developer" in names

    ml_career = next(c for c in careers if c["name"] == "ML Engineer")
    assert len(ml_career["required_skills"]) > 0


def test_auth_register_and_login(client):
    register_res = client.post(
        "/api/auth/register",
        json={
            "name": "Darshak Bisane",
            "email": "darshak@test.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
            "education": "B.Tech Computer Science"
        }
    )
    assert register_res.status_code == 201
    data = register_res.json()
    assert "access_token" in data
    assert data["user"]["name"] == "Darshak Bisane"

    dup_res = client.post(
        "/api/auth/register",
        json={
            "name": "Darshak Bisane",
            "email": "darshak@test.com",
            "password": "securepassword123"
        }
    )
    assert dup_res.status_code == 400

    login_res = client.post(
        "/api/auth/login",
        json={
            "email": "darshak@test.com",
            "password": "securepassword123"
        }
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None


def test_protected_routes_require_token(client):
    res = client.get("/api/users/me")
    assert res.status_code == 401


def test_deterministic_skill_gap_calculation(client, db_session):
    reg = client.post(
        "/api/auth/register",
        json={"name": "Alex Student", "email": "alex@test.com", "password": "password123"}
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = reg.json()["user"]["id"]

    careers_res = client.get("/api/careers")
    ml_career = next(c for c in careers_res.json() if c["name"] == "ML Engineer")
    ml_career_id = ml_career["id"]

    select_res = client.post(
        "/api/users/target-career",
        json={"career_id": ml_career_id},
        headers=headers
    )
    assert select_res.status_code == 200

    gap_res_0 = client.get("/api/skills/gap", headers=headers)
    assert gap_res_0.status_code == 200
    assert gap_res_0.json()["readiness_score"] == 0.0

    skills_to_add = ["Python", "SQL", "Pandas", "NumPy"]
    for s_name in skills_to_add:
        skill = db_session.query(Skill).filter(Skill.name == s_name).first()
        if not skill:
            skill = Skill(name=s_name, category="Test")
            db_session.add(skill)
            db_session.flush()
        db_session.add(StudentSkill(user_id=user_id, skill_id=skill.id))
    db_session.commit()

    gap_res_1 = client.get("/api/skills/gap", headers=headers)
    assert gap_res_1.status_code == 200
    gap_1 = gap_res_1.json()
    assert gap_1["readiness_score"] == 50.0
    assert len(gap_1["matched_skills"]) == 4


def test_roadmap_and_status_update(client, db_session):
    reg = client.post(
        "/api/auth/register",
        json={"name": "Sarah", "email": "sarah@test.com", "password": "password123"}
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    careers_res = client.get("/api/careers")
    fe_career = next(c for c in careers_res.json() if c["name"] == "Frontend Developer")
    client.post("/api/users/target-career", json={"career_id": fe_career["id"]}, headers=headers)

    roadmap_res = client.get("/api/roadmap", headers=headers)
    assert roadmap_res.status_code == 200
    first_item_id = roadmap_res.json()["items"][0]["id"]

    upd_res = client.put(f"/api/roadmap/{first_item_id}", json={"status": "Learning"}, headers=headers)
    assert upd_res.status_code == 200
    assert upd_res.json()["learning_items"] == 1


# ==========================================
# PHASE 2 TESTS (SKILL INTELLIGENCE)
# ==========================================

def test_phase2_1_create_new_skill_and_alias(db_session):
    """Test 1 & 2: New skill can be created, and alias maps to canonical skill."""
    skill, was_created, alias = get_or_create_canonical_skill(
        db=db_session,
        raw_name="MLflow",
        category="AI / Machine Learning"
    )
    assert skill is not None
    assert skill.name == "MLflow"
    assert was_created is True

    # Test alias mapping: "ml flow" or "MLFlow"
    skill2, was_created2, _ = get_or_create_canonical_skill(
        db=db_session,
        raw_name="ml flow"
    )
    assert skill2.id == skill.id
    assert was_created2 is False


def test_phase2_2_alias_normalization(db_session):
    """Test 2: Normalization resolves abbreviations and variants."""
    assert normalize_skill_name("ML") == "Machine Learning"
    assert normalize_skill_name("sklearn") == "Scikit-learn"
    assert normalize_skill_name("reactjs") == "React"
    assert normalize_skill_name("k8s") == "Kubernetes"


def test_phase2_3_evidence_creation_and_repetition(db_session):
    """Test 3 & 4: Evidence is created and repeated mentions increment mention_count."""
    career = db_session.query(Career).filter(Career.name == "ML Engineer").first()
    assert career is not None

    jobs = [
        JobPosting(
            title="Job 1",
            description="Seeking MLflow specialist",
            url="http://example.com/1",
            source="test_api",
            explicit_skills=["MLflow"]
        ),
        JobPosting(
            title="Job 2",
            description="Seeking MLflow engineer",
            url="http://example.com/2",
            source="test_api",
            explicit_skills=["MLflow"]
        )
    ]

    result = process_career_job_postings(career, jobs, db_session)
    assert result["status"] == "success"

    mlflow_skill = db_session.query(Skill).filter(Skill.name == "MLflow").first()
    assert mlflow_skill is not None

    evidence = db_session.query(SkillEvidence).filter(
        SkillEvidence.skill_id == mlflow_skill.id,
        SkillEvidence.career_id == career.id
    ).first()
    assert evidence is not None
    assert evidence.mention_count == 2


def test_phase2_4_skill_promoted_to_careerskill_at_threshold(db_session):
    """Test 5: Skill becomes CareerSkill when mention_count reaches required threshold (5)."""
    career = db_session.query(Career).filter(Career.name == "ML Engineer").first()
    initial_req_count = db_session.query(CareerSkill).filter(CareerSkill.career_id == career.id).count()

    # Provide 5 job postings mentioning MLflow
    jobs = [
        JobPosting(
            title=f"ML Engineer Posting #{i}",
            description="Requires Python, Docker, and MLflow",
            url=f"http://example.com/{i}",
            source="job_board",
            explicit_skills=["Python", "Docker", "MLflow"]
        )
        for i in range(1, 6)
    ]

    result = process_career_job_postings(career, jobs, db_session, required_threshold=5)
    assert "MLflow" in result["updated_requirements"]

    # Verify CareerSkill now exists for MLflow
    mlflow_skill = db_session.query(Skill).filter(Skill.name == "MLflow").first()
    career_skill = db_session.query(CareerSkill).filter(
        CareerSkill.career_id == career.id,
        CareerSkill.skill_id == mlflow_skill.id
    ).first()
    assert career_skill is not None
    assert career_skill.confidence >= 0.85

    new_req_count = db_session.query(CareerSkill).filter(CareerSkill.career_id == career.id).count()
    assert new_req_count == initial_req_count + 1


def test_phase2_5_industry_update_endpoint_with_mock_provider(client, db_session):
    """Test 8: POST /api/industry/update processes mock job market data successfully."""
    # Register student & choose ML Engineer
    reg = client.post(
        "/api/auth/register",
        json={"name": "Dev", "email": "dev@industry.com", "password": "password123"}
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    ml_career = next(c for c in client.get("/api/careers").json() if c["name"] == "ML Engineer")
    client.post("/api/users/target-career", json={"career_id": ml_career["id"]}, headers=headers)

    # Call Industry Update Endpoint
    update_res = client.post(
        "/api/industry/update",
        json={"career": "ML Engineer"},
        headers=headers
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["career"] == "ML Engineer"
    assert data["jobs_processed"] >= 5
    assert "MLflow" in data["skills_detected"]
    assert data["status"] == "success"


def test_phase2_6_industry_insights_endpoint(client, db_session):
    """Test 9: GET /api/industry/{career} returns required and emerging skills."""
    # Run industry update first
    career = db_session.query(Career).filter(Career.name == "ML Engineer").first()
    mock_jobs = MockJobDataProvider.get_jobs_for_career("ML Engineer")
    process_career_job_postings(career, mock_jobs, db_session)

    insights_res = client.get("/api/industry/ML Engineer")
    assert insights_res.status_code == 200
    data = insights_res.json()
    assert data["career"] == "ML Engineer"
    assert len(data["required_skills"]) > 0
    assert len(data["evidence_summary"]) > 0

    req_names = [r["name"] for r in data["required_skills"]]
    assert "MLflow" in req_names


def test_phase2_7_dynamic_readiness_score_impact(client, db_session):
    """Test 6 & 7: Dynamic requirements update propagates to deterministic skill gap score."""
    reg = client.post(
        "/api/auth/register",
        json={"name": "Candidate", "email": "candidate@test.com", "password": "password123"}
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = reg.json()["user"]["id"]

    ml_career = next(c for c in client.get("/api/careers").json() if c["name"] == "ML Engineer")
    client.post("/api/users/target-career", json={"career_id": ml_career["id"]}, headers=headers)

    # Give student 4 skills: Python, SQL, Pandas, NumPy
    for s_name in ["Python", "SQL", "Pandas", "NumPy"]:
        skill = db_session.query(Skill).filter(Skill.name == s_name).first()
        db_session.add(StudentSkill(user_id=user_id, skill_id=skill.id))
    db_session.commit()

    # Initial score: 4 matched out of 8 required = 50.0%
    gap_initial = client.get("/api/skills/gap", headers=headers).json()
    assert gap_initial["readiness_score"] == 50.0
    assert gap_initial["total_required_skills"] == 8

    # Now update industry skills (adds MLflow as 9th required skill)
    client.post("/api/industry/update", json={"career": "ML Engineer"}, headers=headers)

    # Re-check score: 4 matched out of 9 required = 44.4%
    gap_after = client.get("/api/skills/gap", headers=headers).json()
    assert gap_after["total_required_skills"] == 9
    assert gap_after["readiness_score"] == round((4 / 9) * 100, 1)  # 44.4%
    missing_names = [m["name"] for m in gap_after["missing_skills"]]
    assert "MLflow" in missing_names

    # Student learns MLflow!
    mlflow_skill = db_session.query(Skill).filter(Skill.name == "MLflow").first()
    db_session.add(StudentSkill(user_id=user_id, skill_id=mlflow_skill.id))
    db_session.commit()

    # Re-check score: 5 matched out of 9 required = 55.6%
    gap_mastered = client.get("/api/skills/gap", headers=headers).json()
    assert gap_mastered["readiness_score"] == round((5 / 9) * 100, 1)  # 55.6%
    assert "MLflow" in gap_mastered["matched_skills"]


def test_esco_occupation_search(client):
    """Test official European Commission ESCO Web Service occupation search endpoint."""
    res = client.get("/api/esco/occupations/search?q=software developer&limit=3")
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "software developer"
    assert len(data["occupations"]) > 0
    titles = [o["title"].lower() for o in data["occupations"]]
    assert any("software developer" in t for t in titles)


def test_esco_occupation_details(client):
    """Test official ESCO occupation details endpoint."""
    uri = "http://data.europa.eu/esco/occupation/f2b15a0e-e65a-438a-affb-29b9d50b77d1"
    res = client.get(f"/api/esco/occupations/details?uri={uri}")
    assert res.status_code == 200
    data = res.json()
    assert data["title"].lower() == "software developer"
    assert data["essential_count"] > 0
    assert data["optional_count"] > 0
    assert len(data["essential_skills"]) == data["essential_count"]
    assert len(data["optional_skills"]) == data["optional_count"]


def test_esco_ingestion_software_developer(client, db_session):
    """Test ingesting Software Developer occupation + essential and optional skills into DB."""
    res = client.post(
        "/api/esco/occupations/ingest",
        json={"query": "software developer"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["occupation"]["title"].lower() == "software developer"
    assert data["skills_summary"]["essential_count"] == 23
    assert data["skills_summary"]["optional_count"] == 63
    assert data["skills_summary"]["total_count"] == 86

    # Verify directly in DB
    occ = db_session.query(Occupation).filter(Occupation.title == "software developer").first()
    assert occ is not None
    assert occ.code == "2512.3"
    assert occ.esco_uri == "http://data.europa.eu/esco/occupation/f2b15a0e-e65a-438a-affb-29b9d50b77d1"

    # Verify relationships and relation_types
    rels = db_session.query(OccupationSkill).filter(OccupationSkill.occupation_id == occ.id).all()
    assert len(rels) == 86
    essential_rels = [r for r in rels if r.relation_type == "essential"]
    optional_rels = [r for r in rels if r.relation_type == "optional"]
    assert len(essential_rels) == 23
    assert len(optional_rels) == 63

    # Test stored occupation endpoints
    stored_list_res = client.get("/api/esco/occupations/stored")
    assert stored_list_res.status_code == 200
    stored_list = stored_list_res.json()
    assert len(stored_list) >= 1
    assert stored_list[0]["title"] == "software developer"

    stored_detail_res = client.get(f"/api/esco/occupations/stored/{occ.id}")
    assert stored_detail_res.status_code == 200
    stored_detail = stored_detail_res.json()
    assert stored_detail["essential_count"] == 23
    assert stored_detail["optional_count"] == 63


def test_esco_ingestion_idempotency(client, db_session):
    """Test that ingesting the same occupation multiple times does not produce duplicate records."""
    # First ingestion
    client.post("/api/esco/occupations/ingest", json={"query": "software developer"})
    occ_count_1 = db_session.query(Occupation).count()
    skill_count_1 = db_session.query(Skill).count()
    rel_count_1 = db_session.query(OccupationSkill).count()

    # Second ingestion
    res2 = client.post(
        "/api/esco/occupations/ingest",
        json={"uri": "http://data.europa.eu/esco/occupation/f2b15a0e-e65a-438a-affb-29b9d50b77d1"}
    )
    assert res2.status_code == 200

    occ_count_2 = db_session.query(Occupation).count()
    skill_count_2 = db_session.query(Skill).count()
    rel_count_2 = db_session.query(OccupationSkill).count()

    assert occ_count_2 == occ_count_1
    assert skill_count_2 == skill_count_1
    assert rel_count_2 == rel_count_1
