import google.generativeai as genai
import json

def enrich_skills_with_gemini(project_description, model):
    prompt = f"""
    Act as a tech recruiter. Analyze the following project description from a student's resume.
    Extract a list of all plausible technical skills (languages, frameworks, tools) and soft skills (teamwork, leadership, communication) demonstrated in the text.
    Your output MUST be a valid JSON object with a single key "extracted_skills", which is a list of strings.

    Project Description:
    "{project_description}"

    Example:
    Input: "Led a team of 3 to build a web app using React and Firebase for a course project. We presented the final product to the class."
    Output:
    {{
      "extracted_skills": ["React", "Firebase", "Leadership", "Teamwork", "Public Speaking", "Project Management"]
    }}

    Now, generate the JSON for the provided project description:
    """
    
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text).get("extracted_skills", [])
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing enrichment JSON: {e}")
        return []