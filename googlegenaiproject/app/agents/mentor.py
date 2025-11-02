import os
import json

def run_mentor_agent():
    print("\nRunning Mentor Agent...")

    # Base project directory (E:\googlegenaiproject)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    output_dir = os.path.join(base_dir, "outputs")

    # Correct file paths
    skillgap_file = os.path.join(output_dir, "skillgap.json")
    quiz_file = os.path.join(output_dir, "quiz.json")
    mentor_output = os.path.join(output_dir, "mentor_report.json")

    print(f"SkillGap file: {skillgap_file}")
    print(f"Quiz file: {quiz_file}")

    # Verify existence
    missing_files = []
    if not os.path.exists(skillgap_file):
        missing_files.append("skillgap.json")
    if not os.path.exists(quiz_file):
        missing_files.append("quiz.json")

    if missing_files:
        print(f"Missing required input file(s): {', '.join(missing_files)}")
        return

    # Load data safely
    try:
        with open(skillgap_file, "r", encoding="utf-8") as f:
            skillgap_data = json.load(f)
        with open(quiz_file, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)
    except json.JSONDecodeError:
        print("Error: One of the JSON files is not valid JSON.")
        return

    # Generate mentor feedback
    recommendations = {"advice": [], "next_steps": []}

    skill_gaps = skillgap_data.get("inferred_skill_gaps", [])
    if skill_gaps:
        for gap in skill_gaps:
            recommendations["advice"].append(
                f"Focus on improving your {gap} skills through hands-on mini projects."
            )
    else:
        recommendations["advice"].append("No critical skill gaps detected — continue your current learning path.")

    confidence = quiz_data.get("skill_confidence", "").lower()
    if "beginner" in confidence:
        recommendations["next_steps"].append("Start with structured tutorials and beginner-friendly ML projects.")
    elif "intermediate" in confidence:
        recommendations["next_steps"].append("Consolidate your understanding by building real-world applications.")
    elif "advanced" in confidence:
        recommendations["next_steps"].append("Focus on optimization, model deployment, and scaling ML systems.")
    else:
        recommendations["next_steps"].append("Keep learning consistently each week.")

    # Save mentor recommendations
    if os.path.exists(mentor_output):
        os.remove(mentor_output)

    with open(mentor_output, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=4)

    print(f"Mentor recommendations saved to {mentor_output}")

if __name__ == "__main__":
    run_mentor_agent()

