"""RapidAPI Udemy course search integration.

This client hits a RapidAPI wrapper for Udemy course metadata using the
"Course name" endpoint. Configure the following environment variables before
use (see `app/config.py`):

- `RAPIDAPI_KEY`
- `RAPIDAPI_UDEMY_HOST` (e.g. `udemy-course-scrapper-api.p.rapidapi.com`)

The exact response schema may differ per provider plan; `_normalise_course`
handles common fields and ignores unknown ones. Results are mapped to the
shared `CourseItem` schema used by the Course Recommender Agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

from ..config import get_config
from ..schemas import CourseItem


@dataclass
class RapidAPIConfig:
    api_key: Optional[str]
    host: Optional[str]


class UdemyRapidAPI:
    def __init__(self, config: Optional[RapidAPIConfig] = None) -> None:
        if config is None:
            cfg = get_config()
            config = RapidAPIConfig(api_key=cfg.rapidapi_key, host=cfg.rapidapi_udemy_host)
        self.api_key = config.api_key
        self.host = config.host

    def search_courses(self, skills: List[str], max_results_per_skill: int = 3) -> List[CourseItem]:
        if not (self.api_key and self.host):
            return []

        items: List[CourseItem] = []
        for skill in skills:
            skill = skill.strip()
            if not skill:
                continue
            response_data = self._fetch_course_by_name(skill)
            normalised = self._normalise_results(response_data, skill)
            items.extend(normalised[:max_results_per_skill])
        return items

    def _fetch_course_by_name(self, query: str) -> Any:
        url = f"https://{self.host}/course-name"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host,
        }
        params = {"query": query}
        try:
            response = httpx.get(url, headers=headers, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {}

    def _normalise_results(self, payload: Any, skill: str) -> List[CourseItem]:
        if not payload:
            return []

        data: List[Dict[str, Any]] = []
        if isinstance(payload, list):
            data = payload
        elif isinstance(payload, dict):
            # Common structures: {"data": [...]}, {"courses": [...]}, or single item
            for key in ("data", "courses", "result", "items"):
                if isinstance(payload.get(key), list):
                    data = payload[key]
                    break
            else:
                data = [payload]

        items: List[CourseItem] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title = self._choose(entry, ["courseName", "title", "name"])
            url = self._choose(entry, ["courseUrl", "url", "link"])
            if not (title and url):
                continue
            cost = self._parse_cost(self._choose(entry, ["price", "coursePrice", "cost"]))
            duration = self._parse_duration(self._choose(entry, ["duration", "courseDuration"]))
            items.append(
                CourseItem(
                    provider="udemy",
                    course_id=self._choose(entry, ["courseId", "id", "slug"]) or url,
                    title=title,
                    url=url,
                    cost_usd=cost,
                    duration_hours=duration,
                    modality="video",
                    mapped_skills=[skill],
                    priority=15,
                )
            )
        return items

    def _choose(self, entry: Dict[str, Any], keys: List[str]) -> Optional[str]:
        for key in keys:
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _parse_cost(self, value: Optional[str]) -> float:
        if not value:
            return 0.0
        filtered = "".join(ch for ch in value if ch.isdigit() or ch == ".")
        try:
            return float(filtered)
        except ValueError:
            return 0.0

    def _parse_duration(self, value: Optional[str]) -> Optional[int]:
        if not value:
            return None
        digits = "".join(ch for ch in value if ch.isdigit())
        if not digits:
            return None
        try:
            hours = int(digits)
            return hours if hours > 0 else None
        except ValueError:
            return None

