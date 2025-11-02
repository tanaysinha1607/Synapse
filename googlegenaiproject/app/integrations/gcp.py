"""Google Cloud integrations: Firestore persistence.

Firestore collections (by user_id):
- profiles/{user_id}
- skill_graphs/{user_id}
- pcps/{user_id}
- roadmaps/{user_id}
- market_signals/{user_id}
- recommendations/{user_id}
- mentor/{user_id}
- profiler_payload/{user_id}
"""

from __future__ import annotations

from typing import Any, Dict

try:  # pragma: no cover - allow running without GCP deps
    from google.cloud import firestore  # type: ignore
except Exception:  # pragma: no cover
    firestore = None  # type: ignore

from ..schemas import (
    CourseRecommendations,
    MarketSignals,
    MentorSummary,
    ProfilerPayload,
    ResumeProfile,
    Roadmap,
    SkillGraph,
    PCP,
)


class FirestoreClient:
    def __init__(self) -> None:
        # If Firestore client is unavailable, fallback to in-memory store for CLI demo
        if firestore is None:
            self.client = None
            self._memory: Dict[str, Dict[str, Any]] = {}
        else:
            try:
                self.client = firestore.Client()
                self._memory = {}
            except Exception:
                # Fallback if ADC/emulator not configured
                self.client = None
                self._memory = {}

    def _doc(self, collection: str, user_id: str) -> Any:
        if self.client is None:
            key = f"{collection}/{user_id}"
            # Represent a minimal doc-like interface
            class _Doc:
                def __init__(self, store: Dict[str, Dict[str, Any]], k: str) -> None:
                    self.store = store
                    self.k = k

                def set(self, data: Dict[str, Any]) -> None:
                    self.store[self.k] = data

            return _Doc(self._memory, key)
        return self.client.collection(collection).document(user_id)

    def save_resume_profile(self, profile: ResumeProfile) -> None:
        self._doc("profiles", profile.user_id).set(profile.model_dump())

    def save_skill_graph(self, user_id: str, graph: SkillGraph) -> None:
        self._doc("skill_graphs", user_id).set(graph.model_dump())

    def save_pcp(self, pcp: PCP) -> None:
        self._doc("pcps", pcp.user_id).set(pcp.model_dump())

    def save_roadmap(self, roadmap: Roadmap) -> None:
        self._doc("roadmaps", roadmap.user_id).set(roadmap.model_dump())

    def save_market_signals(self, signals: MarketSignals) -> None:
        self._doc("market_signals", signals.user_id).set(signals.model_dump())

    def save_course_recommendations(self, recs: CourseRecommendations) -> None:
        self._doc("recommendations", recs.user_id).set(recs.model_dump())

    def save_mentor_summary(self, summary: MentorSummary) -> None:
        self._doc("mentor", summary.user_id).set(summary.model_dump())

    def save_profiler_payload(self, user_id: str, payload: ProfilerPayload) -> None:
        self._doc("profiler_payload", user_id).set(payload.model_dump())


