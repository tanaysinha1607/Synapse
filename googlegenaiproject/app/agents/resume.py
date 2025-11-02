"""Resume Intelligence Agent

Parses resumes (PDF/DOCX/TXT) and extracts structured entities.
Builds a SkillGraph highlighting strengths and gaps vs. target roles.
"""

from __future__ import annotations
from typing import List, Tuple
import os
import json
from pathlib import Path

from ..schemas import ProfilerPayload, ProfileData, ResumeProfile, SkillEdge, SkillGraph, SkillNode
from ..integrations.parsers import extract_text_from_file


SYSTEM_PROMPT = (
    "You are a Resume Intelligence agent. Extract education, experience, skills, "
    "certifications, projects, and domains from the provided text. Return concise "
    "structured data. If fields are missing, leave them empty."
)

SKILL_LEXICON = {
    "python", "java", "sql", "c++", "javascript", "typescript",
    "react", "django", "flask", "pandas", "numpy", "sklearn",
    "tensorflow", "pytorch", "leadership", "git", "github",
    "docker", "kubernetes", "gcp", "aws",
}

PHRASE_SKILLS = {
    "project management", "machine learning", "data analysis",
    "team leadership", "model deployment",
}


class ResumeIntelligenceAgent:
    def __init__(self) -> None:
        pass

    def parse_and_extract(self, user_id: str, file_path: str) -> Tuple[ResumeProfile, SkillGraph, ProfilerPayload]:
        raw_text = extract_text_from_file(file_path)

        import re
        text_lower = raw_text.lower()
        tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+\-#]+\b", text_lower)

        keyword_skills = {t for t in tokens if t in SKILL_LEXICON}
        for phrase in PHRASE_SKILLS:
            if phrase in text_lower:
                keyword_skills.add(phrase)

        skills = {"general": sorted(keyword_skills)}
        project_descriptions = self._extract_project_descriptions(raw_text)
        experience_summary = self._extract_section_entries(raw_text, {"experience", "work experience"})
        certification_list = self._extract_section_entries(raw_text, {"certifications", "certification"})

        profile = ResumeProfile(
            user_id=user_id,
            raw_text=raw_text[:5000],
            education=[],
            experience=[],
            skills={k: sorted(set(v)) for k, v in skills.items() if v},
            certifications=[],
            projects=[],
            domains=[],
            project_descriptions=project_descriptions,
        )

        nodes: List[SkillNode] = [
            SkillNode(skill_id=s, strength=0.7, source="resume")
            for cat in profile.skills.values()
            for s in cat
        ]
        edges: List[SkillEdge] = []
        graph = SkillGraph(nodes=nodes, edges=edges, gaps={})

        payload = self._build_profiler_payload(profile, experience_summary, certification_list)
        print(json.dumps(payload.dict(), indent=2))

        return profile, graph, payload

    def _extract_project_descriptions(self, raw_text: str) -> List[str]:
        descriptions: List[str] = []
        lines = [line.strip() for line in raw_text.splitlines()]
        capture = False
        for line in lines:
            if line.lower().startswith("projects"):
                capture = True
                continue
            if capture and line and not line.lower().startswith("experience"):
                if line.startswith(("-", "•")):
                    descriptions.append(line.lstrip("-• "))
                elif descriptions and not line.endswith(":"):
                    descriptions[-1] += f" {line}"
            if capture and not line:
                capture = False
        if not descriptions:
            descriptions = [line.lstrip("-• ") for line in lines if line.startswith(("-", "•"))]
        return descriptions[:5]

    def _build_profiler_payload(
        self,
        profile: ResumeProfile,
        experience_summary: List[str],
        certifications: List[str],
    ) -> ProfilerPayload:
        extracted_skills: List[str] = []
        for values in profile.skills.values():
            extracted_skills.extend(values)

        seen = set()
        unique_skills = []
        for s in extracted_skills:
            if s not in seen:
                seen.add(s)
                unique_skills.append(s)

        return ProfilerPayload(
            profile_data=ProfileData(
                extracted_skills=unique_skills,
                project_descriptions=profile.project_descriptions,
                experience_summary=experience_summary,
                certifications=certifications,
            )
        )

    def _extract_section_entries(self, raw_text: str, headers: set[str]) -> List[str]:
        entries: List[str] = []
        lines = [line.strip() for line in raw_text.splitlines()]
        capture = False
        for line in lines:
            lower = line.lower()
            if any(lower.startswith(h) for h in headers):
                capture = True
                continue
            if capture:
                if not line:
                    if entries:
                        break
                    continue
                if any(lower.startswith(h) for h in {"education", "skills", "projects", "summary", "objective"}):
                    break
                if line.startswith(("-", "•")):
                    entries.append(line.lstrip("-• "))
                else:
                    if entries:
                        entries[-1] += f" {line}"
                    else:
                        entries.append(line)
        return entries[:5]


if __name__ == "__main__":
    import sys
    from pathlib import Path
    import json

    # Allow passing a file path or default to sample resume
    resume_file = sys.argv[1] if len(sys.argv) > 1 else "app/samples/resumeanweshsinha.pdf"

    agent = ResumeIntelligenceAgent()

    # Run extraction
    profile, graph, payload = agent.parse_and_extract("user123", resume_file)

    # --- Save extracted skills ---
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    skills_json = {
        "skills": list({s for cat in profile.skills.values() for s in cat})
    }
    out_file = out_dir / "resume_skills.json"
    out_file.write_text(json.dumps(skills_json, indent=2))
    print(f"✅ Saved resume skills to {out_file}")

    # Optional: print top-level summary
    print(f"Extracted {len(skills_json['skills'])} skills:")
    print(", ".join(skills_json["skills"]))




