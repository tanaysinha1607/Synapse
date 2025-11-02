from __future__ import annotations
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Try to import Gemini SDK; if missing, the script will fall back to a local evaluator.
try:
    import google.generativeai as genai  # type: ignore
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False

# Config
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GENAI_API_KEY")
MODEL_NAME = os.getenv("GENAI_MODEL", "gemini-2.0-flash")

# Fixed quiz questions (as provided by frontend)
QUIZ_QUESTIONS = {
    "1": {
        "section": "Career Goal",
        "text": "Which of these best describes your immediate career goal?",
        "options": {
            "a": "Find the highest-paying job, regardless of role.",
            "b": "Secure a role at a top-tier company (e.g., Google, Microsoft).",
            "c": "Join a high-growth startup with high impact and ownership.",
            "d": "Find a role with strong work-life balance and remote options.",
            "e": "I'm exploring and want the best overall match for my skills."
        }
    },
    "2": {
        "section": "Motivation",
        "text": "What is your primary motivator for your next step?",
        "options": {"a": "Learning and Skill Growth", "b": "Salary and Compensation", "c": "Company Prestige and Brand", "d": "Impact and Work Ownership"}
    },
    "3": {
        "section": "5-year Preference",
        "text": "Thinking 5 years ahead, what is more appealing?",
        "options": {"a": "Deep technical mastery (e.g., Principal/Staff Engineer).", "b": "People and team leadership (e.g., Engineering Manager).", "c": "Starting your own company or venture."}
    },
    "4": {
        "section": "Time Commitment",
        "text": "How many hours per week can you realistically commit to upskilling?",
        "options": {"a": "1-3 hours", "b": "4-6 hours", "c": "7-10 hours", "d": "10+ hours"}
    },
    "5": {
        "section": "Learning Style",
        "text": "What's your preferred way to learn a new, complex skill?",
        "options": {"a": "Hands-on projects", "b": "Structured courses", "c": "Reading documentation"}
    },
    "6": {
        "section": "Confidence",
        "text": "When you look at your primary technical skill, how would you rate your confidence?",
        "options": {"a": "Beginner", "b": "Intermediate", "c": "Advanced"}
    },
    "7": {
        "section": "Work Environment",
        "text": "Which work environment sounds most appealing?",
        "options": {"a": "Large structured company", "b": "Fast-paced startup", "c": "Mission-driven organization", "d": "Fully remote and flexible"}
    },
    "8": {
        "section": "Openness to Titles",
        "text": "Are you open to exploring unconventional job titles (e.g., Prompt Engineer)?",
        "options": {"a": "Yes", "b": "No"}
    },
    "9": {
        "section": "Work Type",
        "text": "What kind of work energizes you the most?",
        "options": {"a": "Building and shipping products", "b": "Analyzing data", "c": "Designing/optimizing systems", "d": "Collaborating and solving business problems"}
    },
    "10": {
        "section": "Salary",
        "text": "What is your minimum acceptable annual salary (INR)?",
        "options": None  # free-text numeric
    }
}


def _clean_fenced_markdown(raw: str) -> str:
    if not isinstance(raw, str):
        return ""
    s = raw.strip()
    if s.startswith("```") and s.endswith("```"):
        s = s[3:-3].strip()
    s = s.replace("```json", "").replace("```", "").strip()
    return s


def _call_gemini(prompt: str, model_name: str = MODEL_NAME, max_retries: int = 2):
    if not GENAI_AVAILABLE or not API_KEY:
        raise RuntimeError("Gemini not available or GEMINI_API_KEY missing.")
    genai.configure(api_key=API_KEY)
    # try a couple of model name variants
    candidates = [model_name]
    if model_name.startswith("models/"):
        candidates.append(model_name.split("models/", 1)[-1])
    else:
        candidates.append(f"models/{model_name}")
    last_exc = None
    for name in candidates:
        try:
            model = genai.GenerativeModel(name)
        except Exception as e:
            last_exc = e
            continue
        for attempt in range(1, max_retries + 1):
            try:
                resp = model.generate_content(prompt)
                text = getattr(resp, "text", None)
                if text is None:
                    text = str(resp)
                return text
            except Exception as e:
                last_exc = e
                # if transient, wait and retry
                if "429" in str(e).lower() or "rate limit" in str(e).lower() or "resource exhausted" in str(e).lower():
                    time.sleep(2 * attempt)
                    continue
                break
    raise last_exc or RuntimeError("Failed to call Gemini.")


def _build_prompt(user_id: str, answers: dict) -> str:
    # construct a clear instruction for the model
    lines = [
        "You are an expert career coach. Interpret this user's fixed quiz answers and produce",
        "a JSON object with keys: score_percent, per_question (map of question number to {choice, interpretation, score_1_5}),",
        "persona (short label), summary (2-3 sentences), and recommendations (list of short action items).",
        "Use the fixed questions below (do not invent new questions).",
        "",
        "Fixed Questions (id: question text):"
    ]
    for qid, q in QUIZ_QUESTIONS.items():
        if q["options"]:
            opts = " | ".join([f"{k}: {v}" for k, v in q["options"].items()])
            lines.append(f"{qid}. {q['text']} Options: {opts}")
        else:
            lines.append(f"{qid}. {q['text']} (numeric input expected)")
    lines.append("")
    lines.append("User answers (question_id: selected option or free text):")
    for qid in sorted(QUIZ_QUESTIONS.keys(), key=int):
        val = answers.get(qid, answers.get(str(qid), ""))
        lines.append(f"{qid}: {val}")
    lines.append("")
    lines.append(
        "Return ONLY valid JSON. Score each question on a 1-5 scale; compute score_percent as (sum(scores)/(5*10))*100."
    )
    # example output schema
    lines.append(
        "Output schema example:\n"
        "{\n"
        "  \"score_percent\": 80,\n"
        "  \"per_question\": {\"1\": {\"choice\":\"c\",\"interpretation\":\"likes startups\",\"score\":4}, ...},\n"
        "  \"persona\": \"Startup Builder\",\n"
        "  \"summary\": \"...\",\n"
        "  \"recommendations\": [\"...\",\"...\"]\n"
        "}"
    )
    return "\n".join(lines)


def _deterministic_evaluator(answers: dict):
    # fallback mapping: simple heuristics to produce persona and recommendations
    # map career goal
    goal_map = {
        "a": ("Money Seeker", "Primary focus is compensation."),
        "b": ("Big-Tech Aspirant", "Prefers brand and structure."),
        "c": ("Startup Builder", "Prefers high ownership and impact."),
        "d": ("Work-Life Seeker", "Values balance and remote work."),
        "e": ("Explorer", "Open to matching skills and roles."),
    }
    persona_labels = []
    recommendations = []
    scores = {}
    total_score = 0

    # question 1 -> persona bias
    q1 = answers.get("1", "").lower()
    persona_label, _ = goal_map.get(q1, ("Generalist", ""))
    persona_labels.append(persona_label)

    # learning style (5) and time (4) affect study plan
    q4 = answers.get("4", "b").lower()
    q5 = answers.get("5", "b").lower()
    q6 = answers.get("6", "b").lower()

    # compute per-question pseudo-scores
    for qid in [str(i) for i in range(1, 11)]:
        val = answers.get(qid, "")
        # simple scoring heuristics:
        if qid == "10":
            try:
                sal = int(val.replace(",", "").replace(" ", ""))
                score = 5 if sal <= 1000000 else 4 if sal <= 2000000 else 3
            except Exception:
                score = 3
        else:
            if not val:
                score = 2
            else:
                # prefer "balanced" answers for higher score
                if val.lower() in ("b", "c", "a"):
                    score = 4
                else:
                    score = 3
        scores[qid] = {"choice": val, "interpretation": "", "score": score}
        total_score += score

    # short recommendations based on learning style
    ls = answers.get("5", "b").lower()
    if ls == "a":
        recommendations.append("Prioritize project-based learning and capstone projects.")
    elif ls == "b":
        recommendations.append("Follow a structured course roadmap with checkpoints.")
    else:
        recommendations.append("Use docs and hands-on experiments; supplement with projects.")

    # persona summary
    summary = f"{persona_label}. Recommended focus: {recommendations[0]}"

    percent = round((total_score / (5 * 10)) * 100, 1)
    return {
        "score_percent": percent,
        "per_question": scores,
        "persona": persona_label,
        "summary": summary,
        "recommendations": recommendations
    }


def evaluate_quiz(user_id: str, answers: dict):
    """
    Evaluate quiz answers using Gemini if available, otherwise use deterministic fallback.
    Returns a dict matching the output schema.
    """
    # normalize answer keys to strings "1"..."10"
    ans = {str(k): str(v).strip() for k, v in (answers or {}).items()}

    if GENAI_AVAILABLE and API_KEY:
        prompt = _build_prompt(user_id, ans)
        try:
            raw = _call_gemini(prompt, MODEL_NAME, max_retries=3)
            cleaned = _clean_fenced_markdown(raw)
            # try to extract the first JSON block
            try:
                parsed = json.loads(cleaned)
                return parsed
            except Exception:
                # attempt to find JSON substring
                import re
                m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
                if m:
                    try:
                        parsed = json.loads(m.group(0))
                        return parsed
                    except Exception:
                        pass
                # fallback to returning the raw cleaned text as summary
                return {"score_percent": 0, "per_question": {}, "persona": "LLM-raw", "summary": cleaned[:1000], "recommendations": []}
        except Exception as e:
            # log and fallback
            return {"score_percent": 0, "per_question": {}, "persona": "error", "summary": f"LLM error: {e}", "recommendations": []}
    else:
        # no LLM available; use deterministic fallback
        return _deterministic_evaluator(ans)


def run_quiz_agent(input_path: str | None = None):
    """
    Entrypoint. Reads input JSON, evaluates, and writes app/samples/quiz_report.json.
    """
    default_input = Path("app/samples/quiz_input.json")
    in_path = Path(input_path) if input_path else default_input
    if not in_path.exists():
        print(f"Input file {in_path} not found. Expected structure: {{'user_id':'...', 'answers': {{'1':'a', ...}}}}")
        return

    payload = json.loads(in_path.read_text(encoding="utf-8"))
    user_id = payload.get("user_id", "anonymous")
    answers = payload.get("answers", {})

    # evaluate
    print("Evaluating quiz answers for user:", user_id)
    report = evaluate_quiz(user_id, answers)

    # write output (delete old first)
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "quiz.json"
    if out_file.exists():
        out_file.unlink()
    out_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saved quiz report to {out_file}")
    return report


if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_quiz_agent(arg)
