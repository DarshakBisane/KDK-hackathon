from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# Auth Schemas
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirm_password: Optional[str] = None
    education: Optional[str] = "B.Tech Computer Science"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# User Schemas
class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    education: Optional[str] = None
    student_status: Optional[str] = "Student"
    target_career_id: Optional[int] = None
    target_career_name: Optional[str] = None
    skills: List[str] = []
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    education: Optional[str] = None
    student_status: Optional[str] = None
    target_career_id: Optional[int] = None


class TargetCareerSelect(BaseModel):
    career_id: int


# Career Schemas
class SkillBasic(BaseModel):
    id: int
    name: str
    category: str
    importance: Optional[str] = "HIGH"

    model_config = ConfigDict(from_attributes=True)


class CareerResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    category: str
    required_skills: List[SkillBasic] = []

    model_config = ConfigDict(from_attributes=True)


# Resume Schemas
class ResumeExtraction(BaseModel):
    name: Optional[str] = ""
    education: List[str] = []
    skills: List[str] = []
    projects: List[str] = []
    certifications: List[str] = []
    experience: List[str] = []


class ResumeAnalyzeResponse(BaseModel):
    message: str
    extracted_skills_count: int
    extracted_skills: List[str]
    readiness_score: Optional[float] = None
    target_career: Optional[str] = None


# Skill Gap Schemas
class SkillGapResponse(BaseModel):
    target_career_id: Optional[int] = None
    target_career_name: Optional[str] = None
    readiness_score: float
    matched_skills: List[str]
    missing_skills: List[Dict[str, str]]
    total_required_skills: int
    total_matched_skills: int
    student_skills_count: int


# Dashboard Schemas
class DashboardResponse(BaseModel):
    user_name: str
    student_status: str
    target_career_name: Optional[str] = None
    target_career_id: Optional[int] = None
    readiness_score: float
    strong_skills_count: int
    missing_skills_count: int
    critical_gaps_count: int
    matched_skills: List[str]
    missing_skills: List[Dict[str, str]]
    next_steps: List[str]


# Roadmap Schemas
class RoadmapItemResponse(BaseModel):
    id: int
    title: str
    description: str
    week: int
    status: str
    importance: str
    skill_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RoadmapStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(Not Started|Learning|Completed)$")


class RoadmapProgressResponse(BaseModel):
    total_items: int
    completed_items: int
    learning_items: int
    not_started_items: int
    progress_percentage: float
    items: List[RoadmapItemResponse]
