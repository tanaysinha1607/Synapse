"""Simulated end-to-end flow (CLI)

Steps:
1) User uploads resume (TXT demo).
2) Quiz completes (simulated).
3) Roadmap generated and courses recommended.
4) Market scan updates roadmap.
5) Mentor check-in created.

Run: python -m app.simulate path/to/resume.txt
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple

from rich import print

from .integrations.gcp import FirestoreClient
from .orchestrator import Orchestrator
from .schemas import PCP, ResumeProfile, Roadmap, SkillGraph, ProfilerPayload


def simulate(user_id: str, resume_file: str) -> None:
    store = FirestoreClient()
    orch = Orchestrator(store)

    print("[bold cyan]1) Parsing resume...[/bold cyan]")
    profile, graph, payload = orch.handle_resume_upload(user_id, resume_file)

    print("[bold cyan]2) Running career quiz (simulated)...[/bold cyan]")
    pcp, roadmap, recs, mentor = orch.handle_quiz_complete(user_id, profile, graph)

    print("[bold cyan]3) Initial outputs:[/bold cyan]")
    print({
        "profiler_payload": payload.model_dump(),
        "pcp": pcp.model_dump(),
        "roadmap": roadmap.model_dump(),
        "recommendations": [i.model_dump() for i in recs.items],
        "mentor": mentor.model_dump(),
    })

    print("[bold cyan]4) Market scan and roadmap update...[/bold cyan]")
    market, updated_roadmap, new_recs = orch.scheduled_market_scan(pcp, roadmap, graph)
    print({
        "market": market.model_dump(),
        "roadmap_updated": updated_roadmap.model_dump(),
        "new_recommendations": [i.model_dump() for i in new_recs.items],
    })


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.simulate path/to/resume.txt")
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)
    simulate(user_id="demo-user", resume_file=str(path))


