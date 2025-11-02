import subprocess
import os
import time

# Paths
BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Agents in order
AGENTS = [
    ("Resume Agent", "app.agents.resume"),
    ("Quiz Agent", "app.agents.quiz"),
    ("SkillGap Agent", "app.agents.skill_gap_agent"),
    ("Mentor Agent", "app.agents.mentor"),
    ("Roadmap Agent", "app.agents.roadmap"),  # ✅ ensure roadmap runs last
]

def clear_outputs():
    """Clear old JSON files before new run."""
    print("\n🧹 Clearing old output files...")
    if os.path.exists(OUTPUT_DIR):
        for file in os.listdir(OUTPUT_DIR):
            if file.endswith(".json"):
                os.remove(os.path.join(OUTPUT_DIR, file))
                print(f"  Deleted: {file}")
    else:
        os.makedirs(OUTPUT_DIR)
        print("  Created outputs directory.")
    print("✅ Output cleanup done.\n")

def run_agent(name, module):
    """Run each agent and show progress."""
    print(f"🚀 Running {name}...")
    try:
        subprocess.run(["python", "-m", module], check=True)
        print(f"✅ {name} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {name}: {e}\n")

def main():
    print("\n==============================")
    print("🧠  AI Career Roadmap Pipeline")
    print("==============================\n")

    clear_outputs()

    for name, module in AGENTS:
        run_agent(name, module)
        time.sleep(1)  # brief delay for readability

    print("\n🎯 Pipeline completed! Check your /outputs folder for the latest roadmap.json.\n")

if __name__ == "__main__":
    main()

