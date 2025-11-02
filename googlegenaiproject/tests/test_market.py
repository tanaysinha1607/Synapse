from app.agents.market import MarketIntelligenceAgent
from app.schemas import PCP


def test_market_threshold():
    agent = MarketIntelligenceAgent()
    pcp = PCP(
        user_id="u",
        target_roles=["data analyst"],
        domains=["fintech"],
        weekly_time_hours=8,
        budget_usd=0.0,
        learning_style="video",
        confidence_by_cluster={"python": 0.5},
    )
    market = agent.scan(pcp)
    trending = agent.threshold_exceeded(market, threshold=0.75)
    assert trending, "Expected at least one trending skill above threshold"


