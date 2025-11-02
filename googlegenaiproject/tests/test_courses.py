from app.agents.courses import CourseRecommenderAgent
from app.integrations.courses_api import CourseraAPI, YouTubeAPI
from app.schemas import CourseItem, CourseRecommendations, PCP, Roadmap, RoadmapMilestone, SkillGraph


class FakeUdemy:
    def search_courses(self, skills):  # pragma: no cover - simple stub
        return [
            CourseItem(
                provider="udemy",
                course_id="udemy-python",
                title="Udemy: Python Bootcamp",
                url="https://udemy.com/course/python",
                cost_usd=15.0,
                duration_hours=12,
                modality="video",
                mapped_skills=skills[:1],
                priority=30,
            )
        ]


def test_recommend_provider_priority():
    agent = CourseRecommenderAgent(CourseraAPI(), YouTubeAPI(), FakeUdemy())
    pcp = PCP(
        user_id="u",
        target_roles=["data analyst"],
        domains=["fintech"],
        weekly_time_hours=8,
        budget_usd=100.0,
        learning_style="video",
        confidence_by_cluster={"python": 0.5},
    )
    graph = SkillGraph()
    roadmap = Roadmap(
        user_id="u",
        milestones=[
            RoadmapMilestone(id="m1", title="t1", description="d1", skills=["python", "sql"], estimate_weeks=1),
        ],
        total_estimate_weeks=1,
    )
    recs: CourseRecommendations = agent.recommend(pcp, graph, roadmap)
    assert recs.items, "Expected some recommendations"
    providers = [item.provider for item in recs.items]
    assert providers[0] == "coursera"
    assert "youtube" in providers
    assert "udemy" in providers


