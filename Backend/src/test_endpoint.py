import json
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
import time  # <-- IMPORT TIME

# --- Project Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(BACKEND_DIR) 

ENV_PATH = os.path.join(BACKEND_DIR, '.env')
DATA_DIR = os.path.join(BACKEND_DIR, 'data', 'processed')

# --- Local Module Imports ---
from src.scoring_engine import SynapseScoringEngine
from src.gemini_utils import enrich_skills_with_gemini

# --- 1. One-Time Setup: Load Models and Engine ---
print("--- Initializing Offline Test ---")
load_dotenv(dotenv_path=ENV_PATH) 
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(f"GEMINI_API_KEY not found. Looked for .env file at: {ENV_PATH}")
genai.configure(api_key=api_key)

# Use the correct, full model name from your list
gemini_model = genai.GenerativeModel('models/gemini-pro-latest')

scoring_engine = SynapseScoringEngine(
    data_path=os.path.join(DATA_DIR, 'market_intelligence_db.csv'),
    aspirational_data_path=os.path.join(DATA_DIR, 'aspirational_roles.csv'),
    career_path_model_path=os.path.join(DATA_DIR, 'career_path_model.json')
)
print("--- Initialization Complete. Running tests... ---")


# --- Test Profile 1: "The Salary Hunter" ---
test_profile_1 = {
    "profile_data": {
        "extracted_skills": ["Python", "Pandas", "NumPy", "SQL", "Scikit-learn", "Git"],
        "project_descriptions": [
            "Analyzed sales data using Pandas and SQL to find pricing opportunities.",
            "Built a simple Scikit-learn model to predict customer churn."
        ],
        "experience_summary": ["6-month data analyst internship at a local startup"],
        "certifications": ["Google Data Analytics Certificate"]
    },
    "quiz_data": {
        "career_goal": "top_company",
        "primary_motivator": "salary",
        "future_ambition": "people_leadership",
        "hours_per_week": "7-10",
        "learning_style": "courses",
        "skill_confidence": "intermediate",
        "work_environment": "structured",
        "work_energy": "analyzing_data",
        "min_salary_inr": 800000
    }
}

# --- Test Profile 2: "The Startup Explorer" ---
test_profile_2 = {
    "profile_data": {
        "extracted_skills": ["JavaScript", "React", "HTML", "CSS", "Firebase", "Git"],
        "project_descriptions": [
            "Built a to-do list app with React and Firebase.",
            "Created a personal portfolio website."
        ],
        "experience_summary": ["No formal experience, only class projects."],
        "certifications": []
    },
    "quiz_data": {
        "career_goal": "startup",
        "primary_motivator": "learning",
        "future_ambition": "technical_mastery",
        "hours_per_week": "10+",
        "learning_style": "projects",
        "skill_confidence": "beginner",
        "work_environment": "startup",
        "work_energy": "building_products",
        "min_salary_inr": 300000
    }
}

def run_test(profile_name, payload):
    """
    Simulates the entire API logic without a server.
    """
    print(f"\n" + "="*80)
    print(f"--- RUNNING TEST: {profile_name} ---")
    
    try:
        profile_data = payload.get('profile_data', {})
        quiz_data = payload.get('quiz_data', {})

        # --- 2. Skill Enrichment Logic (from main_api.py) ---
        raw_skills = profile_data.get('extracted_skills', [])
        project_descriptions = profile_data.get('project_descriptions', [])
        
        user_experience = profile_data.get('experience_summary', [])
        user_certifications = profile_data.get('certifications', [])
        
        print(f"Base skills: {raw_skills}")
        enriched_skills = []
        if project_descriptions:
            for desc in project_descriptions:
                if desc:
                    enriched_skills.extend(enrich_skills_with_gemini(desc, gemini_model))
        
        all_user_skills = list(set(raw_skills + enriched_skills))
        print(f"Enriched skills: {all_user_skills}")

        if not all_user_skills:
            print("TEST FAILED: No skills provided or extracted.")
            return

        # --- 3. Run the Scoring Engine (from main_api.py) ---
        print("\nCalling scoring_engine.get_tiered_recommendations...")
        recommendation_payload = scoring_engine.get_tiered_recommendations(
            all_user_skills, 
            user_experience,
            user_certifications,
            quiz_data
        )
        
        print("\n--- TEST COMPLETE: FINAL JSON OUTPUT ---")
        print(json.dumps(recommendation_payload, indent=2))

    except Exception as e:
        print(f"An error occurred during the test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test("Profile 1: The Salary Hunter", test_profile_1)
    
    ### NEW: Wait 60 seconds to respect Free Tier API rate limit
    print("\n--- Waiting 60 seconds to respect Free Tier API rate limit... ---")
    time.sleep(60) 
    
    run_test("Profile 2: The Startup Explorer", test_profile_2)