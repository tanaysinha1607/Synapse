"""
API Schemas and Data Models for Synapse Project
==============================================

This file defines the data structures and API schemas used across all agents.
It ensures consistent communication between the frontend, backend, and AI agents.

Key Components:
- User Profile Schema
- Skill Graph Data Models
- API Request/Response Schemas
- Agent Communication Protocols
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

class SkillCategory(Enum):
    """Categories for skills in the skill graph"""
    TECHNICAL = "technical"
    SOFT = "soft"
    DOMAIN = "domain"
    TOOL = "tool"
    MANUAL = "manual"

class SkillLevel(Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ExperienceLevel(Enum):
    """Overall user experience levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class SkillNode:
    """Represents a skill in the user's skill graph"""
    name: str
    category: SkillCategory
    confidence: float  # 0.0 to 1.0
    source: str  # 'resume', 'video', 'linkedin', 'inferred', 'manual'
    evidence: List[str]  # Supporting evidence for this skill
    level: SkillLevel
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'category': self.category.value,
            'confidence': self.confidence,
            'source': self.source,
            'evidence': self.evidence,
            'level': self.level.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillNode':
        """Create SkillNode from dictionary"""
        return cls(
            name=data['name'],
            category=SkillCategory(data['category']),
            confidence=data['confidence'],
            source=data['source'],
            evidence=data['evidence'],
            level=SkillLevel(data['level'])
        )

@dataclass
class CommunicationStyle:
    """Analysis of user's communication style from video"""
    clarity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    enthusiasm: float  # 0.0 to 1.0
    professionalism: float  # 0.0 to 1.0
    articulation: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'clarity': self.clarity,
            'confidence': self.confidence,
            'enthusiasm': self.enthusiasm,
            'professionalism': self.professionalism,
            'articulation': self.articulation
        }

@dataclass
class UserProfile:
    """Comprehensive user profile built from multimodal inputs"""
    user_id: str
    basic_info: Dict[str, Any]
    skill_graph: List[SkillNode]
    communication_style: Optional[CommunicationStyle]
    career_goals: List[str]
    experience_level: ExperienceLevel
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'basic_info': self.basic_info,
            'skill_graph': [skill.to_dict() for skill in self.skill_graph],
            'communication_style': self.communication_style.to_dict() if self.communication_style else None,
            'career_goals': self.career_goals,
            'experience_level': self.experience_level.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create UserProfile from dictionary"""
        skill_graph = [SkillNode.from_dict(skill_data) for skill_data in data.get('skill_graph', [])]
        
        communication_style = None
        if data.get('communication_style'):
            communication_style = CommunicationStyle(**data['communication_style'])
        
        return cls(
            user_id=data['user_id'],
            basic_info=data.get('basic_info', {}),
            skill_graph=skill_graph,
            communication_style=communication_style,
            career_goals=data.get('career_goals', []),
            experience_level=ExperienceLevel(data.get('experience_level', 'beginner')),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )

# API Request/Response Schemas

@dataclass
class ProcessUserInputsRequest:
    """Request schema for processing user inputs"""
    user_id: str
    resume_content: Optional[str] = None
    resume_file_path: Optional[str] = None
    video_file_path: Optional[str] = None
    linkedin_url: Optional[str] = None
    manual_skills: Optional[List[str]] = None
    career_goals: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ProcessUserInputsResponse:
    """Response schema for processing user inputs"""
    success: bool
    user_profile: Optional[UserProfile] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'user_profile': self.user_profile.to_dict() if self.user_profile else None,
            'error_message': self.error_message
        }

@dataclass
class GetUserProfileRequest:
    """Request schema for retrieving user profile"""
    user_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GetUserProfileResponse:
    """Response schema for retrieving user profile"""
    success: bool
    user_profile: Optional[UserProfile] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'user_profile': self.user_profile.to_dict() if self.user_profile else None,
            'error_message': self.error_message
        }

# Agent Communication Schemas

@dataclass
class AgentRequest:
    """Base schema for agent-to-agent communication"""
    request_id: str
    source_agent: str
    target_agent: str
    timestamp: datetime
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'source_agent': self.source_agent,
            'target_agent': self.target_agent,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data
        }

@dataclass
class AgentResponse:
    """Base schema for agent responses"""
    request_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'success': self.success,
            'data': self.data,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat()
        }

# Specific Agent Communication Schemas

@dataclass
class ProfilerToForecasterRequest:
    """Request from Profiler Agent to Forecaster Agent"""
    user_profile: UserProfile
    target_roles: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_profile': self.user_profile.to_dict(),
            'target_roles': self.target_roles
        }

@dataclass
class ForecasterToSimulationRequest:
    """Request from Forecaster Agent to Simulation Agent"""
    user_profile: UserProfile
    recommended_role: str
    skill_gaps: List[str]
    market_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_profile': self.user_profile.to_dict(),
            'recommended_role': self.recommended_role,
            'skill_gaps': self.skill_gaps,
            'market_data': self.market_data
        }

@dataclass
class SimulationToMentorRequest:
    """Request from Simulation Agent to Mentor Agent"""
    user_profile: UserProfile
    project_brief: str
    user_submission: str
    evaluation_criteria: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_profile': self.user_profile.to_dict(),
            'project_brief': self.project_brief,
            'user_submission': self.user_submission,
            'evaluation_criteria': self.evaluation_criteria
        }

# Frontend API Schemas

@dataclass
class CreateUserRequest:
    """Request to create a new user"""
    user_id: str
    email: str
    name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class UploadFileRequest:
    """Request to upload a file (resume, video)"""
    user_id: str
    file_type: str  # 'resume', 'video'
    file_content: str  # Base64 encoded content
    file_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class UpdateCareerGoalsRequest:
    """Request to update user's career goals"""
    user_id: str
    career_goals: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# Response schemas for frontend

@dataclass
class APIResponse:
    """Standard API response wrapper"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'timestamp': self.timestamp.isoformat()
        }

# Utility functions for schema validation

def validate_skill_node(data: Dict[str, Any]) -> bool:
    """Validate SkillNode data structure"""
    required_fields = ['name', 'category', 'confidence', 'source', 'evidence', 'level']
    
    if not all(field in data for field in required_fields):
        return False
    
    # Validate category
    try:
        SkillCategory(data['category'])
    except ValueError:
        return False
    
    # Validate level
    try:
        SkillLevel(data['level'])
    except ValueError:
        return False
    
    # Validate confidence range
    if not 0.0 <= data['confidence'] <= 1.0:
        return False
    
    return True

def validate_user_profile(data: Dict[str, Any]) -> bool:
    """Validate UserProfile data structure"""
    required_fields = ['user_id', 'skill_graph', 'career_goals', 'experience_level', 'created_at', 'updated_at']
    
    if not all(field in data for field in required_fields):
        return False
    
    # Validate skill_graph
    for skill_data in data.get('skill_graph', []):
        if not validate_skill_node(skill_data):
            return False
    
    # Validate experience_level
    try:
        ExperienceLevel(data['experience_level'])
    except ValueError:
        return False
    
    return True

# Example usage and testing
if __name__ == "__main__":
    # Test schema creation and validation
    skill = SkillNode(
        name="Python",
        category=SkillCategory.TECHNICAL,
        confidence=0.9,
        source="resume",
        evidence=["Built 3 projects using Python"],
        level=SkillLevel.INTERMEDIATE
    )
    
    print("Skill Node:", skill.to_dict())
    print("Validation:", validate_skill_node(skill.to_dict()))
    
    # Test user profile
    profile = UserProfile(
        user_id="test_user",
        basic_info={"name": "Test User"},
        skill_graph=[skill],
        communication_style=None,
        career_goals=["Software Engineer"],
        experience_level=ExperienceLevel.INTERMEDIATE,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    print("\nUser Profile:", profile.to_dict())
    print("Validation:", validate_user_profile(profile.to_dict()))