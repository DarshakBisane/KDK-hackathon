from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.session import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    education = Column(String(200), default="B.Tech in Computer Science")
    student_status = Column(String(100), default="Student")
    target_career_id = Column(Integer, ForeignKey("careers.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    target_career = relationship("Career", back_populates="users")
    student_skills = relationship("StudentSkill", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    roadmap_items = relationship("RoadmapItem", back_populates="user", cascade="all, delete-orphan")


class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), default="Briefcase")
    category = Column(String(50), default="Software Engineering")

    # Relationships
    users = relationship("User", back_populates="target_career")
    career_skills = relationship("CareerSkill", back_populates="career", cascade="all, delete-orphan")
    evidence = relationship("SkillEvidence", back_populates="career")
    trends = relationship("SkillTrend", back_populates="career", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    esco_uri = Column(String(500), unique=True, index=True, nullable=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=True, index=True)
    category = Column(String(50), default="General")
    description = Column(Text, nullable=True)
    skill_type = Column(String(100), nullable=True)
    language = Column(String(10), default="en", nullable=True)
    first_detected_at = Column(DateTime, default=utc_now)
    last_updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    career_skills = relationship("CareerSkill", back_populates="skill", cascade="all, delete-orphan")
    student_skills = relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")
    roadmap_items = relationship("RoadmapItem", back_populates="skill")
    aliases = relationship("SkillAlias", back_populates="skill", cascade="all, delete-orphan")
    evidence = relationship("SkillEvidence", back_populates="skill", cascade="all, delete-orphan")
    trends = relationship("SkillTrend", back_populates="skill", cascade="all, delete-orphan")
    occupation_skills = relationship("OccupationSkill", back_populates="skill", cascade="all, delete-orphan")


class Occupation(Base):
    __tablename__ = "occupations"

    id = Column(Integer, primary_key=True, index=True)
    esco_uri = Column(String(500), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    occupation_skills = relationship("OccupationSkill", back_populates="occupation", cascade="all, delete-orphan")


class OccupationSkill(Base):
    __tablename__ = "occupation_skills"

    id = Column(Integer, primary_key=True, index=True)
    occupation_id = Column(Integer, ForeignKey("occupations.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(50), nullable=False, index=True)  # "essential" or "optional"
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (
        UniqueConstraint("occupation_id", "skill_id", name="uq_occupation_skill"),
    )

    # Relationships
    occupation = relationship("Occupation", back_populates="occupation_skills")
    skill = relationship("Skill", back_populates="occupation_skills")


class SkillAlias(Base):
    __tablename__ = "skill_aliases"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    alias = Column(String(100), unique=True, index=True, nullable=False)
    source = Column(String(50), default="manual")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    skill = relationship("Skill", back_populates="aliases")


class SkillEvidence(Base):
    __tablename__ = "skill_evidence"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="SET NULL"), nullable=True, index=True)
    source = Column(String(50), nullable=False, index=True)
    source_url = Column(String(500), nullable=True)
    evidence_text = Column(Text, nullable=True)
    mention_count = Column(Integer, default=1)
    confidence = Column(Float, default=1.0)
    detected_at = Column(DateTime, default=utc_now, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    skill = relationship("Skill", back_populates="evidence")
    career = relationship("Career", back_populates="evidence")


class SkillTrend(Base):
    __tablename__ = "skill_trends"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False, index=True)
    period = Column(String(20), nullable=False, index=True)  # e.g., '2026-01', '2026-02'
    mention_count = Column(Integer, default=0)
    growth_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    __table_args__ = (
        UniqueConstraint("skill_id", "career_id", "period", name="uq_skill_trends_skill_career_period"),
    )

    # Relationships
    skill = relationship("Skill", back_populates="trends")
    career = relationship("Career", back_populates="trends")


class CareerSkill(Base):
    __tablename__ = "career_skills"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    importance = Column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW
    proficiency_required = Column(String(50), default="Intermediate")
    confidence = Column(Float, default=1.0)
    last_updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    career = relationship("Career", back_populates="career_skills")
    skill = relationship("Skill", back_populates="career_skills")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency = Column(String(50), default="detected")
    source = Column(String(50), default="resume")
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="student_skills")
    skill = relationship("Skill", back_populates="student_skills")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, default=0)
    extracted_data = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="resumes")


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    week = Column(Integer, default=1)
    status = Column(String(30), default="Not Started")  # Not Started, Learning, Completed
    importance = Column(String(20), default="HIGH")
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="roadmap_items")
    skill = relationship("Skill", back_populates="roadmap_items")
