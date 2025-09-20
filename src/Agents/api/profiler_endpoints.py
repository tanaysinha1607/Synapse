"""
Profiler Agent API Endpoints
===========================

This module provides the API endpoints for the Profiler Agent.
It handles all requests related to user profile creation and management.

Key Endpoints:
- POST /api/profiler/process-inputs: Process multimodal user inputs
- GET /api/profiler/profile/{user_id}: Retrieve user profile
- POST /api/profiler/upload-file: Upload resume or video files
- PUT /api/profiler/update-goals: Update career goals
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import base64
import tempfile
import asyncio

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

# Import our schemas and agent
from api.schemas import (
    ProcessUserInputsRequest, ProcessUserInputsResponse,
    GetUserProfileRequest, GetUserProfileResponse,
    CreateUserRequest, UploadFileRequest, UpdateCareerGoalsRequest,
    APIResponse, UserProfile
)
try:
    from crews.profiler.profiler_agent import ProfilerAgent
except Exception:
    # Fallback to legacy location
    from agents.profiler_agent import ProfilerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Synapse Profiler Agent API",
    description="API for processing multimodal user inputs and creating skill graphs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance (initialize with your project ID)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "your-project-id")
profiler_agent = None

async def get_profiler_agent() -> ProfilerAgent:
    """Get or initialize the Profiler Agent instance"""
    global profiler_agent
    if profiler_agent is None:
        profiler_agent = ProfilerAgent(project_id=PROJECT_ID)
    return profiler_agent

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Synapse Profiler Agent API is running", "status": "healthy"}

@app.post("/api/profiler/process-inputs", response_model=ProcessUserInputsResponse)
async def process_user_inputs(request: ProcessUserInputsRequest):
    """
    Process multimodal user inputs and create a comprehensive user profile.
    
    This is the main endpoint that processes all user inputs (resume, video, LinkedIn, etc.)
    and creates a detailed skill graph and user profile.
    """
    try:
        logger.info(f"Processing inputs for user {request.user_id}")
        
        # Get the profiler agent
        agent = await get_profiler_agent()
        
        # Prepare inputs for the agent
        inputs = {
            'career_goals': request.career_goals or []
        }
        
        # Add resume content
        if request.resume_content:
            inputs['resume_file'] = request.resume_content
        elif request.resume_file_path:
            inputs['resume_file'] = request.resume_file_path
        
        # Add other inputs
        if request.video_file_path:
            inputs['video_file'] = request.video_file_path
        if request.linkedin_url:
            inputs['linkedin_url'] = request.linkedin_url
        if request.manual_skills:
            inputs['manual_skills'] = request.manual_skills
        
        # Process inputs
        # Route through CrewAI if enabled
        use_crewai = os.getenv("USE_CREWAI", "0") == "1"
        if use_crewai and hasattr(agent, 'process_user_inputs_crewai'):
            user_profile = await agent.process_user_inputs_crewai(request.user_id, inputs)
        else:
            user_profile = await agent.process_user_inputs(request.user_id, inputs)
        
        return ProcessUserInputsResponse(
            success=True,
            user_profile=user_profile
        )
        
    except Exception as e:
        logger.error(f"Error processing user inputs: {str(e)}")
        return ProcessUserInputsResponse(
            success=False,
            error_message=f"Failed to process user inputs: {str(e)}"
        )

@app.get("/api/profiler/profile/{user_id}", response_model=GetUserProfileResponse)
async def get_user_profile(user_id: str):
    """
    Retrieve a user's profile and skill graph.
    
    Returns the complete user profile including skill graph, communication style,
    and career goals.
    """
    try:
        logger.info(f"Retrieving profile for user {user_id}")
        
        # Get the profiler agent
        agent = await get_profiler_agent()
        
        # Retrieve profile
        user_profile = await agent.get_user_profile(user_id)
        
        if user_profile:
            return GetUserProfileResponse(
                success=True,
                user_profile=user_profile
            )
        else:
            return GetUserProfileResponse(
                success=False,
                error_message=f"No profile found for user {user_id}"
            )
        
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        return GetUserProfileResponse(
            success=False,
            error_message=f"Failed to retrieve user profile: {str(e)}"
        )

@app.post("/api/profiler/upload-file")
async def upload_file(
    user_id: str = Form(...),
    file_type: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a file (resume PDF or video) for processing.
    
    This endpoint handles file uploads and returns the file path for further processing.
    """
    try:
        logger.info(f"Uploading {file_type} file for user {user_id}")
        
        # Validate file type
        if file_type not in ['resume', 'video']:
            raise HTTPException(status_code=400, detail="Invalid file type. Must be 'resume' or 'video'")
        
        # Validate file extension
        file_extension = file.filename.split('.')[-1].lower()
        if file_type == 'resume' and file_extension not in ['pdf', 'txt', 'docx']:
            raise HTTPException(status_code=400, detail="Resume must be PDF, TXT, or DOCX")
        if file_type == 'video' and file_extension not in ['mp4', 'avi', 'mov']:
            raise HTTPException(status_code=400, detail="Video must be MP4, AVI, or MOV")
        
        # Create upload directory
        upload_dir = f"uploads/{user_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = f"{upload_dir}/{file_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File saved to {file_path}")
        
        return APIResponse(
            success=True,
            data={
                "file_path": file_path,
                "file_type": file_type,
                "file_size": len(content),
                "message": "File uploaded successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return APIResponse(
            success=False,
            error=f"Failed to upload file: {str(e)}"
        )

@app.put("/api/profiler/update-goals")
async def update_career_goals(request: UpdateCareerGoalsRequest):
    """
    Update a user's career goals.
    
    This endpoint allows users to update their career goals, which will be used
    by the Forecaster Agent to provide better recommendations.
    """
    try:
        logger.info(f"Updating career goals for user {request.user_id}")
        
        # Get the profiler agent
        agent = await get_profiler_agent()
        
        # Get existing profile
        user_profile = await agent.get_user_profile(request.user_id)
        
        if not user_profile:
            return APIResponse(
                success=False,
                error=f"No profile found for user {request.user_id}"
            )
        
        # Update career goals
        user_profile.career_goals = request.career_goals
        user_profile.updated_at = datetime.now()
        
        # Save updated profile
        await agent._save_profile(user_profile)
        
        return APIResponse(
            success=True,
            data={
                "user_id": request.user_id,
                "career_goals": request.career_goals,
                "message": "Career goals updated successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error updating career goals: {str(e)}")
        return APIResponse(
            success=False,
            error=f"Failed to update career goals: {str(e)}"
        )

@app.post("/api/profiler/analyze-text")
async def analyze_text(
    user_id: str = Form(...),
    text_content: str = Form(...),
    text_type: str = Form(...)  # 'resume', 'project_description', 'cover_letter'
):
    """
    Analyze text content (resume, project description, etc.) and extract skills.
    
    This is a utility endpoint for analyzing any text content and extracting
    relevant skills and information.
    """
    try:
        logger.info(f"Analyzing {text_type} text for user {user_id}")
        
        # Get the profiler agent
        agent = await get_profiler_agent()
        
        # Process the text as if it were a resume
        skills = await agent._process_resume(text_content)
        
        return APIResponse(
            success=True,
            data={
                "user_id": user_id,
                "text_type": text_type,
                "extracted_skills": [skill.to_dict() for skill in skills],
                "skill_count": len(skills)
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        return APIResponse(
            success=False,
            error=f"Failed to analyze text: {str(e)}"
        )

@app.get("/api/profiler/skills/{user_id}")
async def get_user_skills(user_id: str, category: Optional[str] = None):
    """
    Get user's skills, optionally filtered by category.
    
    This endpoint provides a clean view of the user's skill graph,
    useful for the frontend to display skills in different ways.
    """
    try:
        logger.info(f"Retrieving skills for user {user_id}")
        
        # Get the profiler agent
        agent = await get_profiler_agent()
        
        # Get user profile
        user_profile = await agent.get_user_profile(user_id)
        
        if not user_profile:
            return APIResponse(
                success=False,
                error=f"No profile found for user {user_id}"
            )
        
        # Filter skills by category if specified
        skills = user_profile.skill_graph
        if category:
            skills = [skill for skill in skills if skill.category.value == category]
        
        # Group skills by category
        skills_by_category = {}
        for skill in skills:
            cat = skill.category.value
            if cat not in skills_by_category:
                skills_by_category[cat] = []
            skills_by_category[cat].append(skill.to_dict())
        
        return APIResponse(
            success=True,
            data={
                "user_id": user_id,
                "total_skills": len(skills),
                "skills_by_category": skills_by_category,
                "experience_level": user_profile.experience_level.value
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving user skills: {str(e)}")
        return APIResponse(
            success=False,
            error=f"Failed to retrieve user skills: {str(e)}"
        )

@app.delete("/api/profiler/profile/{user_id}")
async def delete_user_profile(user_id: str):
    """
    Delete a user's profile and all associated data.
    
    This endpoint removes all user data from the system.
    """
    try:
        logger.info(f"Deleting profile for user {user_id}")
        
        # Get the profiler agent
        agent = await get_profiler_agent()
        
        # Delete from Firestore
        doc_ref = agent.db.collection('user_profiles').document(user_id)
        doc_ref.delete()
        
        # Clean up uploaded files
        upload_dir = f"uploads/{user_id}"
        if os.path.exists(upload_dir):
            import shutil
            shutil.rmtree(upload_dir)
        
        return APIResponse(
            success=True,
            data={
                "user_id": user_id,
                "message": "Profile deleted successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error deleting user profile: {str(e)}")
        return APIResponse(
            success=False,
            error=f"Failed to delete user profile: {str(e)}"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "profiler_endpoints:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )