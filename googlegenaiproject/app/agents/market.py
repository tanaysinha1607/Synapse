import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Attempt to import Gemini SDK
try:
    import google.generativeai as genai
except Exception as e:
    raise ImportError("google-generativeai is required. Install with: pip install google-generativeai") from e

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY (or GENAI_API_KEY) not found in environment. Add it to .env or env variables.")

genai.configure(api_key=API_KEY)

# model name can be set via env; default to gemini-2.0-flash
ENV_MODEL = os.getenv("GENAI_MODEL", "gemini-2.0-flash")


def _get_model_instance(model_name: str):
    """Create and return a generative model instance; raise if cannot instantiate."""
    try:
        model = genai.GenerativeModel(model_name)
        return model
    except Exception as e:
        # try without "models/" prefix/suffix variants
        alt = model_name
        if model_name.startswith("models/"):
            alt = model_name.split("models/", 1)[-1]
        else:
            alt = f"models/{model_name}"
        try:
            return genai.GenerativeModel(alt)
        except Exception:
            raise RuntimeError(f"Could not instantiate model '{model_name}' or '{alt}': {e}") from e


def _clean_fenced_markdown(raw: str) -> str:
    """Remove common Markdown code fences and language tags like ```json."""
    if not isinstance(raw, str):
        return ""
    s = raw.strip()
    # Remove triple-backtick blocks and language tags
    if s.startswith("```") and s.endswith("```"):
        s = s[3:-3].strip()
    # Remove common language tags
    s = s.replace("```json", "").replace("```python", "").replace("```", "").strip()
    return s


def _call_gemini_with_retries(prompt: str, model_name: str, max_retries: int = 3, backoff: float = 2.0):
    """Call the Gemini model with retries on transient failures like 429."""
    last_exception = None
    model = _get_model_instance(model_name)
    for attempt in range(1, max_retries + 1):
        try:
            resp = model.generate_content(prompt)
            # Prefer .text if present
            text = getattr(resp, "text", None)
            if text is None:
                # fallback: stringify object
                text = str(resp)
            return text
        except Exception as e:
            last_exception = e
            # detect rate-limit or transient errors heuristically by message content
            msg = str(e).lower()
            if "429" in msg or "resource exhausted" in msg or "rate limit" in msg or "quota" in msg:
                wait = backoff * attempt
                print(f"Rate/Quota issue detected (attempt {attempt}/{max_retries}). Waiting {wait}s and retrying...")
                time.sleep(wait)
                continue
            # for other exceptions, break immediately (no retry)
            print(f"Non-retryable error calling Gemini: {e}")
            break
    raise last_exception


def run_market_research_agent():
    """
    Main entrypoint for market research agent.
    Produces outputs/market_insights.json
    """
    print("Running Market Research Agent")
    input_path = Path("outputs/skill_gap_report.json")
    output_path = Path("outputs/market_insights.json")
    # load skill context if available
    if input_path.exists():
        with input_path.open("r", encoding="utf-8") as f:
            try:
                skill_report = json.load(f)
            except Exception:
                skill_report = {}
    else:
        skill_report = {}

    extracted_skills = []
    if isinstance(skill_report, dict):
        # normalized extraction
        missing = skill_report.get("missing_skills", {}) or {}
        # flatten values to a list of candidate skills
        if isinstance(missing, dict):
            for v in missing.values():
                if isinstance(v, list):
                    extracted_skills.extend(v)
                elif isinstance(v, str):
                    extracted_skills.append(v)
        # also include recommendations if present
        recs = skill_report.get("recommendations", {})
    else:
        missing = {}
        recs = {}

    # build a focused prompt for Gemini
    prompt = f"""
You are a market intelligence analyst for technology hiring in 2025. Given the candidate's missing or target skills:
{json.dumps(extracted_skills, indent=2)}

Please produce a concise JSON object with the following keys:
- trending_skills: a list of strings (top 8 skills/tools trending for AI/ML roles right now)
- top_roles: a list of objects {{ "role": string, "demand_reason": string, "skill_priority": [list of skills] }}
- top_tools: list of tools/frameworks in demand
- salary_insights: a list of objects {{ "location": string, "median_inr": number, "notes": string }} (include India metro(s) if relevant)
- hiring_signals: list of short objects {{ "source": string, "signal": string, "confidence": 0-1 }}
- action_recommendations: short actionable bullets for the candidate (max 6)

Return ONLY valid JSON. Keep arrays reasonably sized (no more than 10 items each).
"""

    # attempt to call Gemini with retries
    try:
        raw = _call_gemini_with_retries(prompt, ENV_MODEL, max_retries=3, backoff=3.0)
        cleaned = _clean_fenced_markdown(raw)
        # find first JSON object/array in text using simple heuristics
        json_candidate = None
        try:
            # try direct parse
            json_candidate = json.loads(cleaned)
        except Exception:
            # fallback: search for first {...} or [...]
            import re
            m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
            if m:
                try:
                    json_candidate = json.loads(m.group(0))
                except Exception:
                    json_candidate = None

        if not json_candidate:
            raise ValueError("Could not parse JSON from Gemini response. Raw:\n" + cleaned[:1000])

        insights = json_candidate
    except Exception as e:
        # LLM failed — produce a deterministic fallback stub
        print("LLM market call failed or produced unparseable output:", e)
        # build a reasonable fallback based on missing skills
        fallback_trending = ["python", "pytorch", "tensorflow", "sql", "docker", "kubernetes", "mlops", "cloud"]
        # prefer skills from missing list at front
        for s in extracted_skills:
            s_l = s.lower()
            if s_l not in fallback_trending:
                fallback_trending.insert(0, s_l)
        insights = {
            "trending_skills": fallback_trending[:8],
            "top_roles": [
                {"role": "Machine Learning Engineer", "demand_reason": "High demand for model development and productionization", "skill_priority": ["python", "pytorch", "mlops"]},
                {"role": "Data Scientist", "demand_reason": "Data-driven product teams and analytics needs", "skill_priority": ["python", "sql", "statistics"]},
            ],
            "top_tools": ["PyTorch", "TensorFlow", "scikit-learn", "MLflow", "Docker", "Kubernetes", "BigQuery"],
            "salary_insights": [
                {"location": "Bengaluru", "median_inr": 1500000, "notes": "Typical ranges vary widely by experience and company tier"},
                {"location": "Mumbai", "median_inr": 1400000, "notes": "Financial and product companies pay well"},
            ],
            "hiring_signals": [
                {"source": "LinkedIn Jobs", "signal": "Increase in ML Engineer postings", "confidence": 0.8},
                {"source": "GitHub Activity", "signal": "Rising repos for infra and LLM tooling", "confidence": 0.7},
            ],
            "action_recommendations": [
                "Prioritize hands-on practice with PyTorch and model deployment",
                "Build a small end-to-end project and publish a case study",
                "Learn basic MLOps concepts and Dockerize a model"
            ]
        }

    # Write insights to disk reliably
    try:
        output_dir = Path("outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        # ensure file replace to avoid stale locks
        if (output_dir / "market_insights.json").exists():
            (output_dir / "market_insights.json").unlink()
        with (output_dir / "market_insights.json").open("w", encoding="utf-8") as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        print("Market insights saved to outputs/market_insights.json")
    except Exception as file_err:
        print("Failed to write market_insights.json:", file_err)
        raise

    # Print a simple summary to console for quick inspection
    try:
        ts = insights.get("trending_skills", []) if isinstance(insights, dict) else []
        roles = insights.get("top_roles", []) if isinstance(insights, dict) else []
        print("\nSummary:")
        print("Top trending skills:", (ts[:8] if ts else "N/A"))
        if roles:
            print("Top role example:", roles[0].get("role"), "-", roles[0].get("demand_reason"))
    except Exception:
        pass


if __name__ == "__main__":
    run_market_research_agent()

