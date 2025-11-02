from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
import google.generativeai as genai

# --- NEW: Project Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(BACKEND_DIR) # Add Backend/ to Python path

# Absolute paths
ENV_PATH = os.path.join(BACKEND_DIR, '.env')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data', 'processed')

# --- Local Module Imports ---
from src.scoring_engine import SynapseScoringEngine
from src.gemini_utils import enrich_skills_with_gemini

# --- 1. App Initialization ---
app = Flask(__name__)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}}) 

# --- 2. One-Time Setup: Load Models and Engine ---
print("--- Initializing Synapse Application Server ---")
load_dotenv(dotenv_path=ENV_PATH) # Use absolute path
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(f"GEMINI_API_KEY not found. Looked for .env file at: {ENV_PATH}")
genai.configure(api_key=api_key)

gemini_model = genai.GenerativeModel('models/gemini-pro-latest')

# Load engine with absolute paths
scoring_engine = SynapseScoringEngine(
    data_path=os.path.join(DATA_DIR, 'market_intelligence_db.csv'),
    aspirational_data_path=os.path.join(DATA_DIR, 'aspirational_roles.csv'),
    career_path_model_path=os.path.join(DATA_DIR, 'career_path_model.json')
)
print("--- Initialization Complete. Server is ready. ---")


# --- 3. API Endpoints ---

@app.route('/api/v1/generate_career_plan', methods=['POST', 'OPTIONS'])
def generate_career_plan():
    """
    This is the single, comprehensive endpoint for the entire application.
    """
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return ('', 204, headers)

    try:
        data = request.get_json()

        # 1. Validate Input
        if 'profile_data' not in data or 'quiz_data' not in data:
            return jsonify({"error": "Missing 'profile_data' or 'quiz_data' in request."}), 400
        
        profile_data = data.get('profile_data', {})
        quiz_data = data.get('quiz_data', {})

        # 2. Skill Enrichment
        raw_skills = profile_data.get('extracted_skills', [])
        project_descriptions = profile_data.get('project_descriptions', [])
        
        user_experience = profile_data.get('experience_summary', [])
        user_certifications = profile_data.get('certifications', [])
        
        enriched_skills = []
        if project_descriptions:
            for desc in project_descriptions:
                if desc: 
                    enriched_skills.extend(enrich_skills_with_gemini(desc, gemini_model))
        
        all_user_skills = list(set(raw_skills + enriched_skills))
        
        if not all_user_skills:
            return jsonify({"error": "No skills provided or extracted."}), 400

        # 3. Run the Scoring Engine
        recommendation_payload = scoring_engine.get_tiered_recommendations(
            all_user_skills, 
            user_experience,
            user_certifications,
            quiz_data
        )
        
        if "error" in recommendation_payload:
            return jsonify(recommendation_payload), 404

        # 4. Return the Full Payload
        return jsonify(recommendation_payload), 200

    except Exception as e:
        print(f"An error occurred in /generate_career_plan: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/api/v1/gap_analysis', methods=['POST', 'OPTIONS'])
def gap_analysis():
    # (This endpoint remains unchanged)
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return ('', 204, headers)
        
    try:
        data = request.get_json()
        if 'user_skills' not in data or 'dream_role' not in data:
            return jsonify({"error": "Missing 'user_skills' or 'dream_role'."}), 400
        
        gap_result = scoring_engine.perform_gap_analysis(
            data['user_skills'], 
            data['dream_role'], 
            data.get('dream_company')
        )
        
        if "error" in gap_result:
            return jsonify(gap_result), 404
        
        return jsonify(gap_result), 200

    except Exception as e:
        print(f"An error occurred in /gap_analysis: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)