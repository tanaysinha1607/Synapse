"""Pipeline Orchestrator (CLI-first)

Coordinates agent execution in-order and handles feedback loops. Firestore is
used for persistence. This module provides a simple API for a CLI driver.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from .schemas import (
    CourseRecommendations,
    MarketSignals,
    MentorSummary,
    PCP,
    ResumeProfile,
    Roadmap,
    ProfilerPayload,
    SkillGraph,
)
from .agents.resume import ResumeIntelligenceAgent
from .agents.quiz import CareerQuizAgent
from .agents.roadmap import RoadmapGeneratorAgent
from .agents.market import MarketIntelligenceAgent
from .agents.courses import CourseRecommenderAgent
from .agents.mentor import MentorAgent
from .integrations.courses_api import CourseraAPI, YouTubeAPI
from .integrations.rapidapi_udemy import UdemyRapidAPI
from .integrations.gcp import FirestoreClient


class Orchestrator:
    def __init__(self, firestore: FirestoreClient) -> None:
        self.firestore = firestore
        self.resume_agent = ResumeIntelligenceAgent()
        self.quiz_agent = CareerQuizAgent()
        self.roadmap_agent = RoadmapGeneratorAgent()
        self.market_agent = MarketIntelligenceAgent()
        self.course_agent = CourseRecommenderAgent(CourseraAPI(), YouTubeAPI(), UdemyRapidAPI())
        self.mentor_agent = MentorAgent()

    def handle_resume_upload(self, user_id: str, file_path: str) -> Tuple[ResumeProfile, SkillGraph, ProfilerPayload]:
        profile, skill_graph, payload = self.resume_agent.parse_and_extract(user_id, file_path)
        self.firestore.save_resume_profile(profile)
        self.firestore.save_skill_graph(user_id, skill_graph)
        self.firestore.save_profiler_payload(user_id, payload)
        return profile, skill_graph, payload

    def handle_quiz_complete(self, user_id: str, profile: ResumeProfile, skill_graph: SkillGraph) -> Tuple[PCP, Roadmap, CourseRecommendations, MentorSummary]:
        pcp = self.quiz_agent.simulate_quiz(user_id=user_id, resume_profile=profile)
        self.firestore.save_pcp(pcp)
        roadmap = self.roadmap_agent.generate(pcp, skill_graph)
        self.firestore.save_roadmap(roadmap)
        recs = self.course_agent.recommend(pcp, skill_graph, roadmap)
        # Attach resources to milestones (map by milestone id)
        resource_map: Dict[str, list[str]] = {
            "m1": [i.url for i in recs.items[:3]],
            "m2": [i.url for i in recs.items[3:6]],
            "m3": [i.url for i in recs.items[6:9]],
        }
        roadmap = self.roadmap_agent.attach_resources(roadmap, resource_map)
        self.firestore.save_roadmap(roadmap)
        self.firestore.save_course_recommendations(recs)
        mentor = self.mentor_agent.schedule_checkins(user_id, roadmap)
        self.firestore.save_mentor_summary(mentor)
        return pcp, roadmap, recs, mentor

    def scheduled_market_scan(self, pcp: PCP, roadmap: Roadmap, skill_graph: SkillGraph) -> Tuple[MarketSignals, Roadmap, CourseRecommendations]:
        market = self.market_agent.scan(pcp)
        skills = self.market_agent.threshold_exceeded(market)
        self.firestore.save_market_signals(market)
        if skills:
            roadmap = self.roadmap_agent.update_with_market(roadmap, skills)
            self.firestore.save_roadmap(roadmap)
            recs = self.course_agent.recommend(pcp, skill_graph, roadmap)
            self.firestore.save_course_recommendations(recs)
            return market, roadmap, recs
        return market, roadmap, CourseRecommendations(user_id=pcp.user_id, items=[])


