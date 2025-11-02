from dotenv import load_dotenv
load_dotenv()

import os
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
from datetime import datetime
import json

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_llm(prompt):
    """Send prompt to Gemini 2.0 Flash and return text output."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


def generate_roadmap_content(skillgap_data, mentor_data):
    """Generate a timestamped roadmap using the LLM."""
    prompt = f"""
    You are an AI mentor. Using the following skill gap data and mentor guidance,
    generate an 8-week learning roadmap starting from today's date.

    SKILL GAPS:
    {json.dumps(skillgap_data, indent=2)}

    MENTOR RECOMMENDATIONS:
    {json.dumps(mentor_data, indent=2)}

    Output must be valid JSON in this format:
    {{
      "roadmap": [
        {{
          "week": <number>,
          "start_date": "<YYYY-MM-DD>",
          "focus": "<topic or skill focus>",
          "resources": ["<link or course>", "..."],
          "outcome": "<expected learning result>"
        }}
      ]
    }}
    """

    response = call_llm(prompt)

    try:
        roadmap_json = json.loads(response)
    except json.JSONDecodeError:
        # Fallback: extract JSON portion if wrapped in text
        import re
        match = re.search(r'\{[\s\S]*\}', response)
        if match:
            roadmap_json = json.loads(match.group(0))
        else:
            raise ValueError("Gemini response not valid JSON.")
    return roadmap_json


def run_roadmap_agent():
    print("\nRunning Roadmap Agent...")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    outputs_dir = os.path.join(project_root, "outputs")
    skillgap_file = os.path.join(outputs_dir, "skillgap.json")
    mentor_file = os.path.join(outputs_dir, "mentor_report.json")
    roadmap_file = os.path.join(outputs_dir, "roadmap.json")

    print(f"SkillGap file: {skillgap_file}")
    print(f"Mentor file: {mentor_file}")
    print(f"Roadmap file: {roadmap_file}")

    missing = [f for f in [skillgap_file, mentor_file] if not os.path.exists(f)]
    if missing:
        for f in missing:
            print(f"Missing required file: {f}")
        print("Missing required input files.")
        return

    # Load data
    with open(skillgap_file, "r", encoding="utf-8") as f:
        skillgap_data = json.load(f)
    with open(mentor_file, "r", encoding="utf-8") as f:
        mentor_data = json.load(f)

    # Detect if update is needed
    skillgap_mtime = os.path.getmtime(skillgap_file)
    mentor_mtime = os.path.getmtime(mentor_file)
    if os.path.exists(roadmap_file):
        roadmap_mtime = os.path.getmtime(roadmap_file)
        if roadmap_mtime > max(skillgap_mtime, mentor_mtime):
            print("No changes detected. Roadmap is already up to date.")
            return
        else:
            print("Detected changes in input files. Regenerating roadmap...")

    # Generate new roadmap JSON
    roadmap_data = generate_roadmap_content(skillgap_data, mentor_data)

    # Save output
    with open(roadmap_file, "w", encoding="utf-8") as f:
        json.dump(roadmap_data, f, indent=2)

    print(f"Updated roadmap saved to: {roadmap_file}")
    print("Roadmap generation complete.")


if __name__ == "__main__":
    run_roadmap_agent()

