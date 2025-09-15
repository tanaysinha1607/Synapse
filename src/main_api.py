from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai

# --- Local Module Imports ---
# These are the powerful modules you have already built
from scoring_engine import SynapseScoringEngine
from gemini_utils import enrich_skills_with_gemini

# --- App Initialization ---
app = Flask(__name__)

# --- 1. One-Time Setup: Load Models and Engine ---
# This block runs only ONCE when the server starts.
# It loads all the heavy models into memory for maximum speed on user requests.
print("--- Initializing Synapse Application Server ---")

# Load API Key from .env file for security
load_dotenv(dotenv_path=r'D:\Desktop Data\ML\Projects\Synapse\.env')
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=api_key)

# Initialize the Gemini Model for AI Enrichment
gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Initialize your entire Scoring Engine. This loads all datasets and AI models.
scoring_engine = SynapseScoringEngine()

print("--- Initialization Complete. Server is ready to accept requests. ---")


# --- 2. API Endpoints ---
# These are the "doors" that the frontend application will use to talk to your engine.

@app.route('/recommend', methods=['POST'])
def recommend():
    """
    This is the main endpoint. It takes a user's skills and project descriptions,
    enriches them, and returns the full tiered recommendation with future career paths.
    """
    # --- Onboarding: Get user data from the request ---
    data = request.get_json()
    if not data or 'skills' not in data:
        return jsonify({"error": "Request must include a 'skills' list."}), 400
    
    user_skills = data.get('skills', [])
    project_description = data.get('project_description', '')

    # --- FUNCTIONALITY: AI Skill Enrichment (Idea A) ---
    if project_description:
        print("Enriching skills with Gemini based on project description...")
        additional_skills = enrich_skills_with_gemini(project_description, gemini_model)
        # Combine and remove duplicates for a complete skill profile
        user_skills = list(set(user_skills + additional_skills))
        print(f"Enriched skill set: {user_skills}")

    # --- FUNCTIONALITY: Core Matching & Tiered Output ---
    # This calls your most advanced function, which uses:
    # 1. Skill Knowledge Graphs (Research #1)
    # 2. Cross-Encoder Re-ranking (Research #2)
    # 3. Probabilistic Career Paths (Research #3)
    print("Getting tiered recommendations from the scoring engine...")
    recommendations = scoring_engine.get_tiered_recommendations(user_skills=user_skills)
    
    return jsonify(recommendations)

@app.route('/gap_analysis', methods=['POST'])
def gap_analysis():
    """
    This endpoint is for when a user specifies a dream job.
    It performs a targeted skill gap analysis.
    """
    # --- Onboarding: Get user's dream role (Idea B) ---
    data = request.get_json()
    required_keys = ['skills', 'dream_role', 'dream_company']
    if not data or not all(key in data for key in required_keys):
        return jsonify({"error": "Request must include: skills, dream_role, dream_company."}), 400

    # --- FUNCTIONALITY: Goal-Oriented Trajectory Mapping (Idea B) ---
    print(f"Performing gap analysis for {data['dream_role']} at {data['dream_company']}...")
    analysis_result = scoring_engine.perform_gap_analysis(
        user_skills=data['skills'],
        dream_role=data['dream_role'],
        dream_company=data['dream_company']
    )
    
    return jsonify(analysis_result)


if __name__ == '__main__':
    # To run this server for testing: `python src/main_api.py`
    # Ensure you have Flask installed: `pip install Flask`
    app.run(debug=True, port=5000)

