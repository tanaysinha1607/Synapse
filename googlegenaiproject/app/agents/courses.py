"""Course & Resource Recommendation Agent

Prioritizes Coursera and YouTube. Filters by PCP constraints and ranks.
"""

from __future__ import annotations

from typing import Dict, List

from ..schemas import CourseItem, CourseRecommendations, PCP, Roadmap, SkillGraph
from ..integrations.courses_api import CourseraAPI, YouTubeAPI
from ..integrations.rapidapi_udemy import UdemyRapidAPI


SYSTEM_PROMPT = (
    "You are a Course Recommender. Given PCP, SkillGraph, and Roadmap, return a "
    "sequenced list of courses/resources that fit budget, time, and modality."
)


class CourseRecommenderAgent:
    def __init__(
        self,
        coursera: CourseraAPI,
        youtube: YouTubeAPI,
        udemy: UdemyRapidAPI | None = None,
    ) -> None:
        self.coursera = coursera
        self.youtube = youtube
        self.udemy = udemy or UdemyRapidAPI()

    def recommend(self, pcp: PCP, skill_graph: SkillGraph, roadmap: Roadmap) -> CourseRecommendations:
        items: List[CourseItem] = []

        # Gather candidate skills from roadmap
        target_skills: List[str] = []
        for m in roadmap.milestones:
            target_skills.extend(m.skills)
        target_skills = list(dict.fromkeys(target_skills))

        # Query providers
        items.extend(self.coursera.search_courses(target_skills))
        items.extend(self.youtube.search_videos(target_skills))
        items.extend(self.udemy.search_courses(target_skills))

        # Filter by budget (keep free or within budget)
        filtered = [i for i in items if i.cost_usd <= pcp.budget_usd]

        # Sort by provider preference then priority
        provider_rank = {"coursera": 0, "youtube": 1, "udemy": 2}
        filtered.sort(key=lambda i: (provider_rank.get(i.provider, 9), i.priority))

        # Simple sequencing: first N matching early milestones
        return CourseRecommendations(user_id=pcp.user_id, items=filtered[:12])


