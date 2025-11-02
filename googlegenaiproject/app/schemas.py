"""Pydantic data models for the multi-agent career guidance system.

These models define IO contracts between agents and storage shapes for
Firestore. Keep them stable for frontend integration. Include brief sample JSON
shapes in comments where useful for React + Chart.js.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class EducationEntry(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class ExperienceEntry(BaseModel):
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class Certification(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[int] = None


class ProjectEntry(BaseModel):
    name: str
    description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    user_id: str
    raw_text: Optional[str] = None
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    skills: Dict[str, List[str]] = Field(default_factory=dict)  # category->skills
    certifications: List[Certification] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    project_descriptions: List[str] = Field(default_factory=list)


class SkillNode(BaseModel):
    skill_id: str
    strength: float = 0.0  # 0-1 normalized
    source: str = "resume|quiz|inferred"


class SkillEdge(BaseModel):
    pair: Tuple[str, str]
    weight: float = 0.0


class SkillGraph(BaseModel):
    nodes: List[SkillNode] = Field(default_factory=list)
    edges: List[SkillEdge] = Field(default_factory=list)
    gaps: Dict[str, List[str]] = Field(default_factory=dict)  # target_role -> missing skills


class PCP(BaseModel):
    user_id: str
    target_roles: List[str]
    domains: List[str]
    weekly_time_hours: int
    budget_usd: float
    learning_style: str  # video | project | self-paced | blended
    confidence_by_cluster: Dict[str, float]  # 0-1 per cluster


class RoadmapMilestone(BaseModel):
    id: str
    title: str
    description: str
    skills: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)  # course IDs/URLs
    estimate_weeks: int = 1
    dependencies: List[str] = Field(default_factory=list)
    checkpoint: bool = False


class Roadmap(BaseModel):
    user_id: str
    version: int = 1
    milestones: List[RoadmapMilestone] = Field(default_factory=list)
    total_estimate_weeks: int = 0

    # Sample JSON (frontend expects):
    # {
    #   "milestones": [
    #     {
    #       "id": "m1",
    #       "title": "Python Fundamentals",
    #       "estimate_weeks": 2,
    #       "skills": ["python", "data structures"],
    #       "resources": ["yt:xyz", "c:abc"],
    #       "dependencies": []
    #     }
    #   ],
    #   "total_estimate_weeks": 16
    # }


class MarketSignal(BaseModel):
    skill: str
    score: float
    source: str
    timestamp: str


class MarketSignals(BaseModel):
    user_id: str
    role: Optional[str] = None
    signals: List[MarketSignal] = Field(default_factory=list)


class CourseItem(BaseModel):
    provider: str  # coursera | youtube
    course_id: str
    title: str
    url: str
    cost_usd: float = 0.0
    duration_hours: Optional[int] = None
    modality: str = "video"
    mapped_skills: List[str] = Field(default_factory=list)
    priority: int = 100


class CourseRecommendations(BaseModel):
    user_id: str
    items: List[CourseItem] = Field(default_factory=list)


class MentorSummary(BaseModel):
    user_id: str
    week: int
    progress_by_milestone: Dict[str, float] = Field(default_factory=dict)
    blockers: List[str] = Field(default_factory=list)
    nudges: List[str] = Field(default_factory=list)


class ProfileData(BaseModel):
    extracted_skills: List[str] = Field(default_factory=list)
    project_descriptions: List[str] = Field(default_factory=list)
    experience_summary: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


class ProfilerPayload(BaseModel):
    profile_data: ProfileData


