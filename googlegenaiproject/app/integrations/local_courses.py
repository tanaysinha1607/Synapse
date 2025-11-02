"""Course provider API stubs for Coursera and YouTube.

Replace these with real API calls (Secrets via Secret Manager). For now, return
deterministic mock data to demonstrate ranking and filtering.
"""

from __future__ import annotations

from typing import List

from ..schemas import CourseItem


class CourseraAPI:
    def search_courses(self, skills: List[str]) -> List[CourseItem]:
        items: List[CourseItem] = []
        for idx, s in enumerate(skills):
            items.append(
                CourseItem(
                    provider="coursera",
                    course_id=f"c-{s}",
                    title=f"Coursera: {s.title()} Specialization",
                    url=f"https://coursera.org/learn/{s}",
                    cost_usd=39.0,
                    duration_hours=12,
                    modality="video",
                    mapped_skills=[s],
                    priority=10 + idx,
                )
            )
        return items


class YouTubeAPI:
    def search_videos(self, skills: List[str]) -> List[CourseItem]:
        items: List[CourseItem] = []
        for idx, s in enumerate(skills):
            items.append(
                CourseItem(
                    provider="youtube",
                    course_id=f"yt-{s}",
                    title=f"YouTube: {s.title()} Crash Course",
                    url=f"https://youtube.com/results?search_query={s}",
                    cost_usd=0.0,
                    duration_hours=4,
                    modality="video",
                    mapped_skills=[s],
                    priority=20 + idx,
                )
            )
        return items


