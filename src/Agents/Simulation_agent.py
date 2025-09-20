import vertexai
from vertexai.generative_models import GenerativeModel

def get_simulation_agent_brief(user_background: str, chosen_role: str) -> str:
    """
    Generates a personalized 'Micro-Internship' project brief.
    
    Args:
        user_background: A description of the user's skills and background.
        chosen_role: The career path the user has selected.
        
    Returns:
        A string containing the generated project brief.
    """
    # Initialize Vertex AI
    vertexai.init(project="your-gcp-project-id", location="your-region")
    model = GenerativeModel("gemini-1.0-pro")

    # The prompt for the Simulation Agent
    simulation_prompt = f"""
    You are a senior strategist at a leading company. A new junior team member, a {user_background}, has expressed interest in the role of {chosen_role}. Your task is to give them a bite-sized, realistic project they can complete in one evening to show they have the skills for this role.
    
    Generate a "Micro-Internship" project brief. The brief should include:
    Project Title: A short, compelling title for the task.
    Background: A brief, engaging overview of the company's mission and the project's importance.
    Your Mission: A clear, concise description of the task. The task should be tangible and produce a portfolio-ready deliverable.
    Key Deliverable: Specify the final output and its format.
    Resources: Provide a short, curated list of learning resources (e.g., "A relevant Google Scholar paper," "A key YouTube video from a top expert") to help them get started.
    
    Focus on creating a project that feels real and challenging but is also achievable within a short timeframe.
    """
    
    response = model.generate_content(simulation_prompt)
    return response.text

if __name__ == '__main__':
    # --- Example Usage ---
    user_skill = "literature student with a passion for storytelling"
    career_path = "Narrative Designer"
    
    print(f"Generating a project brief for a {user_skill} aiming to be a {career_path}...")
    project_brief = get_simulation_agent_brief(user_skill, career_path)
    print("\n--- Generated Project Brief ---\n")
    print(project_brief)