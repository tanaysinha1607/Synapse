"""Test script for Resume Intelligence Agent."""

from app.agents.resume import ResumeIntelligenceAgent
from pathlib import Path


def main():
    # Change this if your PDF file has a different name or location
    test_file = Path("tests/resumeanweshsinha.pdf")

    if not test_file.exists():
        print(f"❌ Resume file not found at: {test_file.resolve()}")
        return

    print("=== Running Resume Intelligence Agent ===\n")

    agent = ResumeIntelligenceAgent()
    profile, graph, payload = agent.parse_and_extract(
        user_id="anwesh",
        file_path=str(test_file)
    )

    print("\n--- PROFILE ---")
    print(profile)

    print("\n--- SKILL GRAPH ---")
    print(graph)

    print("\n--- PROFILER PAYLOAD ---")
    print(payload)


if __name__ == "__main__":
    main()
