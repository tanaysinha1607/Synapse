from app.agents.roadmap import RoadmapGeneratorAgent
from app.schemas import PCP, SkillGraph


def test_generate_basic_roadmap():
    agent = RoadmapGeneratorAgent()
    pcp = PCP(
        user_id="u",
        target_roles=["data analyst"],
        domains=["fintech"],
        weekly_time_hours=8,
        budget_usd=0.0,
        learning_style="video",
        confidence_by_cluster={"python": 0.5},
    )
    graph = SkillGraph()
    roadmap = agent.generate(pcp, graph)
    assert roadmap.milestones, "Expected milestones in roadmap"
    assert roadmap.total_estimate_weeks > 0


