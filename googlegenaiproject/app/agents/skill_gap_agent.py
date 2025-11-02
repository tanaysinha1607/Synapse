import json
from pathlib import Path
from datetime import datetime
import re
import sys

# ------------ Helpers to find project root and outputs dir ------------
def find_project_root_with_outputs(max_levels: int = 5) -> Path:
    """
    Start from this file's directory and walk up until we find a directory
    that contains an 'outputs' folder. If not found, fall back to cwd if it
    contains outputs. Otherwise return the parent-parent (best guess).
    """
    start = Path(__file__).resolve()
    for i, p in enumerate(start.parents):
        if i >= max_levels:
            break
        if (p / "outputs").exists():
            return p
    # fallback: check cwd
    cwd = Path.cwd()
    if (cwd / "outputs").exists():
        return cwd
    # last-resort: use third parent if available, else topmost parent
    if len(start.parents) >= 3:
        return start.parents[2]
    return start.parents[-1]

# determine project root
PROJECT_ROOT = find_project_root_with_outputs()
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

RESUME_FILE = OUTPUTS_DIR / "resume_skills.json"
QUIZ_FILE = OUTPUTS_DIR / "quiz_report.json"
OUTPUT_FILE = OUTPUTS_DIR / "skillgap.json"

# Print diagnostics
print("Project root (resolved):", PROJECT_ROOT)
print("Outputs directory:", OUTPUTS_DIR)
print("Resume file expected at:", RESUME_FILE)
print("Quiz file expected at:", QUIZ_FILE)
print("Skillgap output will be:", OUTPUT_FILE)
print()

# ---------- Utility functions ----------
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

def extract_skills(resume_text: str) -> list[str]:
    tech_skills = [
        "python", "c++", "java", "javascript", "html", "css",
        "react", "node", "sql", "mysql", "mongodb", "pandas",
        "numpy", "machine learning", "deep learning", "data analysis",
        "tensorflow", "pytorch", "ai", "nlp", "computer vision",
    ]
    found = [s for s in tech_skills if s in resume_text]
    return sorted(set(found))

def infer_gaps_from_quiz(quiz_data: dict) -> list[str]:
    gaps = []
    # defensive: quiz_data may contain nested structure, normalize to a flat map of answers if possible
    # Accept either quiz_data being the direct answers dict, or a wrapper with "answers"
    if "answers" in quiz_data and isinstance(quiz_data["answers"], dict):
        q = {k.lower(): str(v).lower() for k, v in quiz_data["answers"].items()}
    else:
        q = {k.lower(): str(v).lower() for k, v in quiz_data.items()}

    if "structured" in q.get("5", "") or "structured" in q.get("preferred_way_to_learn", ""):
        gaps.append("self-paced problem-solving")
    if "hands-on" in q.get("5", "") or "hands-on" in q.get("preferred_way_to_learn", ""):
        gaps.append("theoretical understanding")
    if "1-3" in q.get("4", "") or "1-3" in q.get("hours_per_week", ""):
        gaps.append("consistent learning habits")
    if "beginner" in q.get("6", "") or "beginner" in q.get("skill_confidence", ""):
        gaps.append("project experience")

    return sorted(set(gaps))

# ---------- Main ----------
def run_skillgap_agent() -> None:
    print("Running SkillGap Agent...\n")

    # ensure outputs dir exists (may not, which explains many issues)
    if not OUTPUTS_DIR.exists():
        print("Outputs directory does not exist at:", OUTPUTS_DIR)
        print("Creating outputs directory.")
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # show current files in outputs for debugging
    existing = sorted([p.name for p in OUTPUTS_DIR.iterdir() if p.is_file()])
    print("Files currently in outputs/:", existing)
    print()

    # Load resume file
    if not RESUME_FILE.exists():
        print("Missing resume_skills.json at the expected path.")
        print("Please ensure the resume agent wrote resume_skills.json into the project-level outputs/ directory.")
        return
    try:
        resume_data = json.loads(RESUME_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print("Failed to read/parse resume_skills.json:", e)
        return

    # Normalize resume text and extract skills
    resume_text = clean_text(json.dumps(resume_data))
    resume_skills = extract_skills(resume_text)

    # Load quiz file (allow alternative name if present)
    if not QUIZ_FILE.exists():
        # try alternative common names
        alt = OUTPUTS_DIR / "quiz.json"
        alt2 = OUTPUTS_DIR / "quiz_report.json"
        if alt.exists():
            quiz_path = alt
        elif alt2.exists():
            quiz_path = alt2
        else:
            print("Missing quiz report. Expected quiz_report.json (or quiz.json) in outputs/.")
            return
    else:
        quiz_path = QUIZ_FILE

    try:
        quiz_data = json.loads(quiz_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to read/parse {quiz_path.name}:", e)
        return

    # Infer gaps
    quiz_gaps = infer_gaps_from_quiz(quiz_data)

    # Combine insights
    base_gaps = [
        "deploying models",
        "data preprocessing",
        "real-world project exposure"
    ]
    all_gaps = sorted(set(base_gaps + quiz_gaps))

    recommended_courses = [
        "Caltech ML Fundamentals",
        "Fast.ai Practical Deep Learning",
        "DataCamp Data Preprocessing Track"
    ]

    result = {
        "timestamp": datetime.now().isoformat(),
        "resume_skills": resume_skills,
        "quiz_indicated_gaps": quiz_gaps,
        "inferred_skill_gaps": all_gaps,
        "recommended_courses": recommended_courses,
    }

    # Write output safely (overwrite)
    try:
        OUTPUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except Exception as e:
        print("Failed to write skillgap.json:", e)
        return

    print("skillgap.json created at:", OUTPUT_FILE)
    print("\nPreview of result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    run_skillgap_agent()
