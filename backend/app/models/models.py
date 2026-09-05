from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
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


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), default="General")

    # Relationships
    career_skills = relationship("CareerSkill", back_populates="skill", cascade="all, delete-orphan")
    student_skills = relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")
    roadmap_items = relationship("RoadmapItem", back_populates="skill")


class CareerSkill(Base):
    __tablename__ = "career_skills"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    importance = Column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW

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
