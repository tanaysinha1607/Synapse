# Import agents
from Agents.Mentor_agent import get_mentor_agent_feedback
from Agents.Simulation_agent import get_simulation_agent_brief
from Agents.crews.profiler.profiler_agent import ProfilerAgent

# Import other modules
from Agents.api.schemas import (
    SkillNode,
    SkillCategory,
    SkillLevel,
    UserProfile,
    ExperienceLevel,
    CommunicationStyle,
    ProcessUserInputsRequest,
    ProcessUserInputsResponse,
    GetUserProfileRequest,
    GetUserProfileResponse,
    CreateUserRequest,
    UploadFileRequest,
    UpdateCareerGoalsRequest,
    APIResponse,
)
from Agents.scripts.run_profiler_demo import main as run_profiler_demo


from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import google.generativeai as genai

# --- Local Module Imports ---
# These are the powerful modules you have already built
from scoring_engine import SynapseScoringEngine
from gemini_utils import enrich_skills_with_gemini

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# --- App Initialization ---
app = Flask(__name__)
@app.route("/", methods=["GET"])
def health_check():
    return {"message": "Synapse Profiler Agent API is running", "status": "healthy"}


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
# --- New API Endpoint: Onboard User (The Profiler Agent) ---
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Temporary in-memory user store
user_profiles = {}

@app.route('/onboard', methods=['POST'])
def onboard():
    """
    Onboard user and store profile in memory.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    user_data = data.get("user_data", {})

    if not user_id or not user_data:
        return jsonify({"error": "Missing user_id or user_data"}), 400

    # Store user profile in memory
    user_profiles[user_id] = user_data

    return jsonify({
        "status": "success",
        "user_id": user_id,
        "profile": user_data
    })
@app.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    profile = user_profiles.get(user_id)
    if not profile:
        return jsonify({"error": "User not found"}), 404
    return jsonify(profile)

@app.route("/upload_resume", methods=["POST", "OPTIONS"])
def upload_resume():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    try:
        data = request.get_json()
        user_id = data.get("user_id")
        resume_file = data.get("resume_file")  # base64 string, file path, or just filename (depending on frontend)

        # ⚡️ Hackathon simplification: just echo back
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "message": "Resume uploaded successfully",
            "resume_file": resume_file
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400
@app.route("/upload_video", methods=["POST", "OPTIONS"])
def upload_video():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    try:
        data = request.get_json()
        user_id = data.get("user_id")
        video_file = data.get("video_file")  # base64 string, file path, or just filename

        return jsonify({
            "status": "success",
            "user_id": user_id,
            "message": "Video uploaded successfully",
            "video_file": video_file
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Returns combined dashboard data:
    - user profile (dummy for now, or pull from DB if available)
    - recommendations (calls scoring engine)
    - gap analysis (optional if not requested)
    """
    try:
        # Example: hardcoded user profile for now
        user_profile = {
            "user_id": "amardeep001",
            "career_goals": "Backend Engineer",
            "skills": ["Python", "Flask"]
        }

        # Generate recommendations
        recommendations = scoring_engine.get_tiered_recommendations(user_profile["skills"])

        # Perform gap analysis for a default role
        gap = scoring_engine.perform_gap_analysis(
            user_skills=user_profile["skills"],
            dream_role="Backend Developer",
            dream_company=""
        )

        return jsonify({
            "profile": user_profile,
            "recommendations": recommendations,
            "gap_analysis": gap
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- New API Endpoint: Simulate Career Path (The Simulation Agent) ---
@app.route('/simulate', methods=['POST', 'OPTIONS'])
def simulate_user_path():
    """
    Endpoint: Simulate a user's career path based on their background and chosen role.
    """

    # --- Handle CORS Preflight ---
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    try:
        # --- Parse Request ---
        data = request.get_json()
        if not data or "career_choice" not in data:
            return jsonify({"error": "Missing 'career_choice' in request."}), 400

        user_background = data.get("user_background", "a generic user")

        # --- Run Simulation ---
        project = get_simulation_agent_brief(user_background, data["career_choice"])

        response = jsonify({"project_brief": project})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500



# --- New API Endpoint: Provide Feedback (The Mentor Agent) ---
@app.route('/mentor', methods=['POST', 'OPTIONS'])
def get_feedback():
    """
    Endpoint: Provide feedback on a user's submission for a chosen role.
    """

    # --- Handle CORS Preflight ---
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    try:
        # --- Parse Request ---
        data = request.get_json()
        if not data or "submission" not in data or "chosen_role" not in data:
            return jsonify({"error": "Missing 'submission' or 'chosen_role' in request."}), 400

        # --- Run Mentor Agent ---
        feedback = get_mentor_agent_feedback(data["chosen_role"], data["submission"])

        response = jsonify({"feedback": feedback})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500


import json   
    
import numpy as np

@app.route('/recommend', methods=['POST', 'OPTIONS'])
def recommend():
    """
    Recommend career paths based on user skills and project description.
    """

    # --- Handle CORS Preflight ---
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    try:
        # --- Parse request ---
        data = request.get_json()
        if not data or "skills" not in data:
            return jsonify({"error": "Request must include a 'skills' list."}), 400

        user_skills = data.get("skills", [])
        project_description = data.get("project_description", "")

        # --- AI skill enrichment ---
        if project_description:
            print("Enriching skills with Gemini based on project description...")
            additional_skills = enrich_skills_with_gemini(project_description, gemini_model)
            user_skills = list(set(user_skills + additional_skills))
            print(f"Enriched skill set: {user_skills}")

        # --- Core matching ---
        print("Getting tiered recommendations from the scoring engine...")
        recommendations = scoring_engine.get_tiered_recommendations(user_skills=user_skills)

        # --- Fix JSON serialization issue ---
        def convert(o):
            if isinstance(o, (np.float32, np.float64)):
                return float(o)
            if isinstance(o, (np.int32, np.int64)):
                return int(o)
            return str(o)

        response = app.response_class(
            response=json.dumps(recommendations, default=convert),
            status=200,
            mimetype="application/json"
        )
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500



@app.route('/gap_analysis', methods=['POST', 'OPTIONS'])
def gap_analysis():
    """
    Endpoint: Perform a targeted skill gap analysis for a dream job.
    """

    # --- Handle CORS Preflight (OPTIONS) ---
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    try:
        # --- Parse Input ---
        data = request.get_json()
        required_keys = ["skills", "dream_role", "dream_company"]

        if not data or not all(key in data for key in required_keys):
            return jsonify({
                "error": "Request must include: skills, dream_role, dream_company."
            }), 400

        # --- Perform Gap Analysis ---
        print(f"Performing gap analysis for {data['dream_role']} at {data['dream_company']}...")
        analysis_result = scoring_engine.perform_gap_analysis(
            user_skills=data["skills"],
            dream_role=data["dream_role"],
            dream_company=data["dream_company"]
        )

        response = jsonify(analysis_result)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500



if __name__ == '__main__':
    # To run this server for testing: `python src/main_api.py`
    # Ensure you have Flask installed: `pip install Flask`
    app.run(debug=True,host="0.0.0.0", port=8000)

