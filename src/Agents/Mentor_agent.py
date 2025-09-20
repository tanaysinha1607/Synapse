import vertexai
from vertexai.generative_models import GenerativeModel

def get_mentor_agent_feedback(chosen_role: str, user_submission: str) -> str:
    """
    Provides constructive feedback on a user's project submission.
    
    Args:
        chosen_role: The career path the user is pursuing.
        user_submission: The user's submitted project content.
        
    Returns:
        A string containing the personalized feedback.
    """
    # Initialize Vertex AI
    vertexai.init(project="your-gcp-project-id", location="your-region")
    model = GenerativeModel("gemini-1.0-pro")

    # The prompt for the Mentor Agent, including the rubric
    mentor_prompt = f"""
    You are a senior manager with deep expertise in {chosen_role}. You are reviewing a submission from a junior team member who is trying to learn {chosen_role}. The junior has just submitted their first attempt at a project.
    
    Your task is to provide constructive feedback based on a rubric. The feedback should be:
    1. Encouraging: Start with positive feedback, highlighting what the user did well.
    2. Constructive: Identify one or two key areas for improvement. Phrase these as helpful suggestions, not criticisms.
    3. Actionable: Provide a specific, concrete suggestion on how they can improve the submission.
    4. Persona: Use a professional, supportive, and Socratic tone.
    
    Rubric for Evaluation:
    * Clarity: Is the submission easy to understand?
    * Relevance: Does it directly address the project brief?
    * Skill Demonstration: Does it show a foundational understanding of the core skills for this role?
    
    Review the following user submission and provide feedback:
    ---
    {user_submission}
    ---
    """
    
    response = model.generate_content(mentor_prompt)
    return response.text

if __name__ == '__main__':
    # --- Example Usage ---
    career_path = "Narrative Designer"
    example_submission = """
    My character's name is Pip, a squirrel who loves to collect nuts. He lives in a magical forest where the trees are sad because of pollution. The story is about how he and his friends try to make the trees happy again by singing songs. I've attached a draft of the first three dialogue interactions.
    """
    
    print(f"Generating mentor feedback for a user's submission on a {career_path} project...")
    mentor_feedback = get_mentor_agent_feedback(career_path, example_submission)
    print("\n--- Generated Mentor Feedback ---\n")
    print(mentor_feedback)