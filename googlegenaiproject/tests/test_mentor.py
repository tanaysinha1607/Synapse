from app.agents.mentor import MentorAgent
from app.schemas import Roadmap, RoadmapMilestone


def test_schedule_and_log_progress():
    agent = MentorAgent()
    roadmap = Roadmap(
        user_id="u",
        milestones=[
            RoadmapMilestone(id="m1", title="t1", description="d1", estimate_weeks=1),
            RoadmapMilestone(id="m2", title="t2", description="d2", estimate_weeks=1),
        ],
        total_estimate_weeks=2,
    )
    summary = agent.schedule_checkins("u", roadmap)
    assert summary.progress_by_milestone == {"m1": 0.0, "m2": 0.0}
    updated = agent.log_progress(summary, {"m1": 0.5, "m2": 1.0})
    assert updated.progress_by_milestone["m1"] == 0.5
    assert updated.progress_by_milestone["m2"] == 1.0


