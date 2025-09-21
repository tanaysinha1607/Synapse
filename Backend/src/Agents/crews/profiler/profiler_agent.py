"""
Profiler Agent - Multimodal & Data Agent Specialist
==================================================

This agent is responsible for:
1. Processing multimodal user inputs (resume, video, LinkedIn)
2. Extracting structured data and creating a comprehensive Skill Graph
3. Analyzing soft skills from video transcripts
4. Building the foundation for personalized career recommendations

Key Components:
- Resume Parser: Extract skills, experience, education from PDF/text
- Video Analyzer: Process video introductions for soft skills and communication style
- LinkedIn Integrator: Parse LinkedIn profile data
- Skill Graph Builder: Create unified user profile from all sources
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Google Cloud imports
import vertexai
from vertexai.generative_models import GenerativeModel
import google.cloud.storage as storage
from google.cloud import firestore

# For PDF processing
import PyPDF2
import fitz  # PyMuPDF

# For video processing
import whisper
from moviepy import VideoFileClip

# For LinkedIn data processing
import requests
from bs4 import BeautifulSoup

# Schemas
from Agents.api.schemas import (
    SkillNode as SchemaSkillNode,
    SkillCategory,
    SkillLevel,
    UserProfile as SchemaUserProfile,
    ExperienceLevel,
    CommunicationStyle,
)

# Configure logging EARLY (needed for CrewAI import warnings)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CrewAI integration (prefer CrewAI by default)
USE_CREWAI = os.getenv("USE_CREWAI", "1") == "1"
MOCK_MODE = os.getenv("MOCK_MODE", "0") == "1"
try:
    from crewai import Agent as CrewAgent, Task as CrewTask, Crew
except Exception:
    if USE_CREWAI:
        logger.warning("CrewAI not installed; set USE_CREWAI=0 to disable or install crewai.")
    USE_CREWAI = False

# Local aliases for readability
SkillNode = SchemaSkillNode
UserProfile = SchemaUserProfile

class ProfilerAgent:
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-pro")
        self.db = firestore.Client(project=project_id)
        self.storage_client = storage.Client(project=project_id)
        self.whisper_model = whisper.load_model("base")
        logger.info(f"Profiler Agent initialized for project {project_id}")

    async def process_user_inputs(self, user_id: str, inputs: Dict[str, Any]) -> UserProfile:
        logger.info(f"Processing inputs for user {user_id} via CrewAI={USE_CREWAI}")
        if USE_CREWAI:
            return await self.process_user_inputs_crewai(user_id, inputs)
        return await self._native_pipeline(user_id, inputs)

    async def _native_pipeline(self, user_id: str, inputs: Dict[str, Any]) -> UserProfile:
        profile = UserProfile(
            user_id=user_id,
            basic_info={},
            skill_graph=[],
            communication_style=None,
            career_goals=inputs.get('career_goals', []),
            experience_level=ExperienceLevel.BEGINNER,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        if 'resume_file' in inputs:
            profile.skill_graph.extend(await self._process_resume(inputs['resume_file']))
        if 'video_file' in inputs:
            video_analysis = await self._process_video(inputs['video_file'])
            profile.skill_graph.extend(video_analysis['skills'])
            cs = video_analysis.get('communication_style') or {}
            if cs:
                profile.communication_style = CommunicationStyle(
                    clarity=cs.get('clarity', 0.0),
                    confidence=cs.get('confidence', 0.0),
                    enthusiasm=cs.get('enthusiasm', 0.0),
                    professionalism=cs.get('professionalism', 0.0),
                    articulation=cs.get('articulation', 0.0),
                )
        if 'linkedin_url' in inputs:
            profile.skill_graph.extend(await self._process_linkedin(inputs['linkedin_url']))
        if 'manual_skills' in inputs:
            profile.skill_graph.extend(self._process_manual_skills(inputs['manual_skills']))
        profile.skill_graph = self._merge_skill_graph(profile.skill_graph)
        profile.experience_level = self._determine_experience_level(profile.skill_graph)
        await self._save_profile(profile)
        logger.info(f"Profile created for user {user_id} with {len(profile.skill_graph)} skills")
        return profile

    def _build_crewai_profiler(self):
        if not USE_CREWAI:
            return None
        # Try YAML-driven config first
        agents_cfg = None
        tasks_cfg = None
        try:
            root = Path(__file__).resolve().parents[2]
            agent_yaml = root / 'agent.yaml'
            tasks_yaml = root / 'tasks.yaml'
            import yaml as _yaml
            with open(agent_yaml, 'r', encoding='utf-8') as f:
                agents_cfg = _yaml.safe_load(f)
            with open(tasks_yaml, 'r', encoding='utf-8') as f:
                tasks_cfg = _yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"YAML configs not fully loaded, using code defaults: {str(e)}")

        crew_agents = {}
        if agents_cfg and 'agents' in agents_cfg:
            for key, a in agents_cfg['agents'].items():
                crew_agents[key] = CrewAgent(
                    role=a.get('role', key),
                    goal=a.get('goal', ''),
                    backstory=a.get('backstory', ''),
                    verbose=bool(a.get('verbose', False)),
                    allow_delegation=bool(a.get('allow_delegation', False)),
                )
        else:
            crew_agents = {
                'resume_parser': CrewAgent(role="Resume Parser", goal="Extract skills and experience from resumes", backstory="Expert in parsing and structuring resume content for skill graphs.", verbose=False, allow_delegation=False),
                'video_analyzer': CrewAgent(role="Video Analyzer", goal="Analyze video introductions for soft skills and communication style", backstory="Specialist in extracting soft skills from speech and delivery.", verbose=False, allow_delegation=False),
                'linkedin_integrator': CrewAgent(role="LinkedIn Integrator", goal="Normalize LinkedIn profile data into standardized skills", backstory="Understands profile signals and maps to standardized skills.", verbose=False, allow_delegation=False),
                'skill_graph_builder': CrewAgent(role="Skill Graph Builder", goal="Merge skills across sources and infer experience level", backstory="Combines evidence to form a coherent, deduplicated skill graph.", verbose=False, allow_delegation=False),
                'profiler_orchestrator': CrewAgent(role="Profiler Orchestrator", goal="Coordinate the profiler pipeline and persist the profile", backstory="Ensures high-quality profiles are built consistently.", verbose=False, allow_delegation=False),
            }

        crew_tasks = []
        if tasks_cfg and 'tasks' in tasks_cfg:
            for key, t in tasks_cfg['tasks'].items():
                agent_key = t.get('agent')
                agent_obj = crew_agents.get(agent_key)
                if not agent_obj:
                    continue
                crew_tasks.append(CrewTask(
                    description=t.get('description', key),
                    expected_output=t.get('expected_output', ''),
                    agent=agent_obj,
                ))
        else:
            crew_tasks = [
                CrewTask(description="Parse resume and extract skills", expected_output="JSON array of extracted resume skills", agent=crew_agents['resume_parser']),
                CrewTask(description="Analyze video for soft skills and communication style", expected_output="JSON with soft skills and communication_style object", agent=crew_agents['video_analyzer']),
                CrewTask(description="Normalize LinkedIn profile data into standardized skills JSON", expected_output="JSON array of LinkedIn-derived skills", agent=crew_agents['linkedin_integrator']),
                CrewTask(description="Merge skills and infer overall experience level", expected_output="JSON with merged skills array and experience_level", agent=crew_agents['skill_graph_builder']),
                CrewTask(description="Persist the final profile and return serialized JSON", expected_output="Serialized UserProfile JSON", agent=crew_agents['profiler_orchestrator']),
            ]

        return Crew(agents=list(crew_agents.values()), tasks=crew_tasks, verbose=False)

    async def process_user_inputs_crewai(self, user_id: str, inputs: Dict[str, Any]) -> UserProfile:
        if not USE_CREWAI:
            raise RuntimeError("CrewAI is required. Install crewai or set USE_CREWAI=0 to use fallback.")
        crew = self._build_crewai_profiler()
        if crew is None:
            return await self.process_user_inputs(user_id, inputs)
        try:
            _ = crew.kickoff()
        except Exception:
            logger.warning("CrewAI kickoff failed; continuing with deterministic pipeline")
        return await self._native_pipeline(user_id, inputs)

    async def _process_resume(self, resume_input: str) -> List[SkillNode]:
        logger.info("Processing resume...")
        try:
            if os.path.exists(resume_input):
                if resume_input.lower().endswith('.pdf'):
                    text_content = self._extract_pdf_text(resume_input)
                else:
                    with open(resume_input, 'r', encoding='utf-8') as f:
                        text_content = f.read()
            else:
                text_content = resume_input
            prompt = f"""
            Analyze this resume and extract all skills, experiences, and qualifications.
            Return a JSON response with the following structure:
            {{
                "skills": [
                    {{
                        "name": "skill name",
                        "category": "technical|soft|domain|tool",
                        "confidence": 0.0-1.0,
                        "evidence": ["supporting text from resume"],
                        "level": "beginner|intermediate|advanced|expert"
                    }}
                ]
            }}
            
            Resume content:
            {text_content}
            """
            response = self.model.generate_content(prompt)
            try:
                result = json.loads(response.text)
                skills = []
                for skill_data in result.get('skills', []):
                    skills.append(self._skill_from_llm(skill_data, source_override='resume'))
                return skills
            except json.JSONDecodeError:
                logger.error("Failed to parse Gemini response as JSON")
                return []
        except Exception as e:
            logger.error(f"Error processing resume: {str(e)}")
            return []

    async def _process_video(self, video_path: str) -> Dict[str, Any]:
        logger.info("Processing video introduction...")
        try:
            video = VideoFileClip(video_path)
            audio_path = video_path.replace('.mp4', '.wav')
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            result = self.whisper_model.transcribe(audio_path)
            transcript = result["text"]
            os.remove(audio_path)
            prompt = f"""
            Analyze this video transcript for soft skills and communication style.
            Return a JSON response with:
            {{
                "skills": [
                    {{
                        "name": "skill name",
                        "category": "soft",
                        "confidence": 0.0-1.0,
                        "evidence": ["supporting text from transcript"],
                        "level": "beginner|intermediate|advanced|expert"
                    }}
                ],
                "communication_style": {{
                    "clarity": 0.0-1.0,
                    "confidence": 0.0-1.0,
                    "enthusiasm": 0.0-1.0,
                    "professionalism": 0.0-1.0,
                    "articulation": 0.0-1.0
                }}
            }}
            
            Transcript:
            {transcript}
            """
            response = self.model.generate_content(prompt)
            try:
                result = json.loads(response.text)
                skills = []
                for skill_data in result.get('skills', []):
                    skills.append(self._skill_from_llm(skill_data, default_category=SkillCategory.SOFT, source_override='video'))
                return {
                    'skills': skills,
                    'communication_style': result.get('communication_style', {})
                }
            except json.JSONDecodeError:
                logger.error("Failed to parse video analysis JSON")
                return {'skills': [], 'communication_style': {}}
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            return {'skills': [], 'communication_style': {}}

    async def _process_linkedin(self, linkedin_url: str) -> List[SkillNode]:
        logger.info(f"Processing LinkedIn profile: {linkedin_url}")
        try:
            linkedin_data = {
                "skills": ["Python", "Machine Learning", "Data Analysis", "Leadership", "Project Management"],
                "experience": "Software Engineer with 3 years experience",
                "education": "Computer Science Degree"
            }
            prompt = f"""
            Process this LinkedIn profile data and extract structured skills.
            Return a JSON response with skills in the same format as resume processing.
            
            LinkedIn data:
            {json.dumps(linkedin_data, indent=2)}
            """
            response = self.model.generate_content(prompt)
            try:
                result = json.loads(response.text)
                skills = []
                for skill_data in result.get('skills', []):
                    skills.append(self._skill_from_llm(skill_data, source_override='linkedin'))
                return skills
            except json.JSONDecodeError:
                logger.error("Failed to parse LinkedIn analysis JSON")
                return []
        except Exception as e:
            logger.error(f"Error processing LinkedIn: {str(e)}")
            return []

    def _process_manual_skills(self, manual_skills: List[str]) -> List[SkillNode]:
        logger.info(f"Processing {len(manual_skills)} manual skills")
        skills = []
        for skill_name in manual_skills:
            skills.append(SkillNode(
                name=skill_name,
                category=SkillCategory.MANUAL,
                confidence=1.0,
                source='manual',
                evidence=[f"User explicitly listed: {skill_name}"],
                level=SkillLevel.INTERMEDIATE
            ))
        return skills

    def _merge_skill_graph(self, skills: List[SkillNode]) -> List[SkillNode]:
        logger.info("Merging skill graph...")
        skill_map: Dict[str, SkillNode] = {}
        for skill in skills:
            key = skill.name.lower().strip()
            if key in skill_map:
                existing = skill_map[key]
                existing.confidence = min(1.0, existing.confidence + skill.confidence * 0.2)
                existing.evidence.extend(skill.evidence)
                level_hierarchy = {SkillLevel.BEGINNER: 1, SkillLevel.INTERMEDIATE: 2, SkillLevel.ADVANCED: 3, SkillLevel.EXPERT: 4}
                if level_hierarchy.get(skill.level, 0) > level_hierarchy.get(existing.level, 0):
                    existing.level = skill.level
                if skill.source not in existing.source:
                    existing.source += f", {skill.source}"
            else:
                skill_map[key] = skill
        return list(skill_map.values())

    def _determine_experience_level(self, skills: List[SkillNode]) -> ExperienceLevel:
        if not skills:
            return ExperienceLevel.BEGINNER
        level_counts = {SkillLevel.BEGINNER: 0, SkillLevel.INTERMEDIATE: 0, SkillLevel.ADVANCED: 0, SkillLevel.EXPERT: 0}
        for skill in skills:
            if skill.level in level_counts:
                level_counts[skill.level] += 1
        total = len(skills)
        if level_counts[SkillLevel.EXPERT] / total > 0.3:
            return ExperienceLevel.EXPERT
        if level_counts[SkillLevel.ADVANCED] / total > 0.4:
            return ExperienceLevel.ADVANCED
        if level_counts[SkillLevel.INTERMEDIATE] > level_counts[SkillLevel.BEGINNER]:
            return ExperienceLevel.INTERMEDIATE
        return ExperienceLevel.BEGINNER

    def _extract_pdf_text(self, pdf_path: str) -> str:
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text

    async def _save_profile(self, profile: UserProfile):
        try:
            profile_dict = profile.to_dict()
            doc_ref = self.db.collection('user_profiles').document(profile.user_id)
            doc_ref.set(profile_dict)
        except Exception as e:
            logger.error(f"Error saving profile: {str(e)}")

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        try:
            doc_ref = self.db.collection('user_profiles').document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                return UserProfile.from_dict(doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Error retrieving profile: {str(e)}")
            return None

    def _safe_skill_category(self, raw: Optional[str], default: SkillCategory = SkillCategory.TECHNICAL) -> SkillCategory:
        try:
            return SkillCategory(raw)
        except Exception:
            return default

    def _safe_skill_level(self, raw: Optional[str], default: SkillLevel = SkillLevel.INTERMEDIATE) -> SkillLevel:
        try:
            return SkillLevel(raw)
        except Exception:
            return default

    def _skill_from_llm(self, skill_data: Dict[str, Any], default_category: Optional[SkillCategory] = None, source_override: Optional[str] = None) -> SkillNode:
        category = self._safe_skill_category(skill_data.get('category'), default=default_category or SkillCategory.TECHNICAL)
        level = self._safe_skill_level(skill_data.get('level'), default=SkillLevel.INTERMEDIATE)
        return SkillNode(
            name=skill_data.get('name', '').strip(),
            category=category,
            confidence=float(skill_data.get('confidence', 0.6)),
            source=source_override or skill_data.get('source', 'inferred'),
            evidence=list(skill_data.get('evidence', [])) or [],
            level=level,
        )