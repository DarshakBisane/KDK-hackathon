import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.database.seed import seed_database
from app.main import app
from app.models.models import User, Skill, StudentSkill, CareerSkill

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

    # Check that ML Engineer has required skills
    ml_career = next(c for c in careers if c["name"] == "ML Engineer")
    assert len(ml_career["required_skills"]) > 0


def test_auth_register_and_login(client):
    # Register
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

    # Duplicate registration should fail
    dup_res = client.post(
        "/api/auth/register",
        json={
            "name": "Darshak Bisane",
            "email": "darshak@test.com",
            "password": "securepassword123"
        }
    )
    assert dup_res.status_code == 400

    # Login
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
    # Me endpoint without token
    res = client.get("/api/users/me")
    assert res.status_code == 401


def test_deterministic_skill_gap_calculation(client, db_session):
    # 1. Register user
    reg = client.post(
        "/api/auth/register",
        json={
            "name": "Alex Student",
            "email": "alex@test.com",
            "password": "password123"
        }
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = reg.json()["user"]["id"]

    # 2. Get ML Engineer Career ID
    careers_res = client.get("/api/careers")
    ml_career = next(c for c in careers_res.json() if c["name"] == "ML Engineer")
    ml_career_id = ml_career["id"]

    # 3. Select ML Engineer as target career
    select_res = client.post(
        "/api/users/target-career",
        json={"career_id": ml_career_id},
        headers=headers
    )
    assert select_res.status_code == 200
    assert select_res.json()["target_career_name"] == "ML Engineer"

    # 4. Check initial gap with 0 student skills
    gap_res_0 = client.get("/api/skills/gap", headers=headers)
    assert gap_res_0.status_code == 200
    gap_0 = gap_res_0.json()
    assert gap_0["readiness_score"] == 0.0
    assert len(gap_0["matched_skills"]) == 0
    assert len(gap_0["missing_skills"]) == len(ml_career["required_skills"])

    # 5. Insert known skills for user (e.g. Python, SQL, Pandas, NumPy)
    skills_to_add = ["Python", "SQL", "Pandas", "NumPy"]
    for s_name in skills_to_add:
        skill = db_session.query(Skill).filter(Skill.name == s_name).first()
        if not skill:
            skill = Skill(name=s_name, category="Test")
            db_session.add(skill)
            db_session.flush()
        db_session.add(StudentSkill(user_id=user_id, skill_id=skill.id))
    db_session.commit()

    # 6. Re-check deterministic gap
    # ML Engineer has 8 required skills in seed data (Python, Machine Learning, Scikit-learn, Deep Learning, SQL, NumPy, Pandas, Docker)
    # Matched: Python, SQL, Pandas, NumPy = 4
    # Readiness = (4 / 8) * 100 = 50.0%
    gap_res_1 = client.get("/api/skills/gap", headers=headers)
    assert gap_res_1.status_code == 200
    gap_1 = gap_res_1.json()
    assert gap_1["readiness_score"] == 50.0
    assert len(gap_1["matched_skills"]) == 4
    assert len(gap_1["missing_skills"]) == 4
    missing_names = [m["name"] for m in gap_1["missing_skills"]]
    assert "Machine Learning" in missing_names
    assert "Scikit-learn" in missing_names
    assert "Deep Learning" in missing_names
    assert "Docker" in missing_names


def test_roadmap_and_status_update(client, db_session):
    # Register and select career
    reg = client.post(
        "/api/auth/register",
        json={"name": "Sarah", "email": "sarah@test.com", "password": "password123"}
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    careers_res = client.get("/api/careers")
    fe_career = next(c for c in careers_res.json() if c["name"] == "Frontend Developer")
    client.post("/api/users/target-career", json={"career_id": fe_career["id"]}, headers=headers)

    # Get roadmap
    roadmap_res = client.get("/api/roadmap", headers=headers)
    assert roadmap_res.status_code == 200
    roadmap_data = roadmap_res.json()
    assert roadmap_data["total_items"] > 0
    assert roadmap_data["progress_percentage"] == 0.0

    first_item = roadmap_data["items"][0]
    first_item_id = first_item["id"]

    # Update status to Learning
    upd_res = client.put(
        f"/api/roadmap/{first_item_id}",
        json={"status": "Learning"},
        headers=headers
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["learning_items"] == 1

    # Update status to Completed
    upd_res_2 = client.put(
        f"/api/roadmap/{first_item_id}",
        json={"status": "Completed"},
        headers=headers
    )
    assert upd_res_2.status_code == 200
    assert upd_res_2.json()["completed_items"] == 1
    assert upd_res_2.json()["progress_percentage"] > 0.0
