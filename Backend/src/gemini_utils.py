import google.generativeai as genai
import json
import re

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
        
        # More robust parsing
        if not response.parts:
            print("Error: Gemini response was empty (possibly safety settings).")
            return []

        # Clean the response text to remove markdown and find the JSON
        cleaned_text = response.text.strip()
        json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
        
        if not json_match:
            print(f"Error: No JSON object found in Gemini response. Text was: {cleaned_text}")
            return []

        cleaned_json = json_match.group(0)
        return json.loads(cleaned_json).get("extracted_skills", [])
    
    except (json.JSONDecodeError, AttributeError, Exception) as e:
        print(f"Error parsing enrichment JSON: {e}")
        return []

def create_skill_graph(skill_list, job_title, model):
    skills_str = ", ".join(f"'{skill}'" for skill in skill_list)
    
    prompt = f"""
    You are a senior technical recruiter, skills taxonomy expert, and JSON structuring specialist.
    Your task is to analyze a raw list of skills for the role {job_title} and organize them into a clean, hierarchical JSON object.
    Output only a valid JSON object, no explanations, no comments, no extra text.
    Top-level keys must be skill categories such as:
    "Programming Languages", "Frameworks & Libraries", "Databases", "Cloud Platforms", 
    "Developer Tools", "Key Concepts", "Soft Skills"
    The value of each category should be an array of strings.
    Your response must be only the JSON object.
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_text)
    except (json.JSONDecodeError, AttributeError, Exception) as e:
        print(f"Error creating skill graph for {job_title}: {e}")
        return None

def generate_career_path_probabilities(role_title, model):
    prompt = f"""
    Act as an expert career analyst for the Indian tech industry.
    For a person currently in an entry-level (0-2 years experience) role as a '{role_title}', what are the three most likely next career steps?
    Your output MUST be a valid JSON object. The keys should be the next job titles, and the values should be their approximate probability as a float, summing to 1.0. 
    Do not include any explanations, just the JSON object.

    Example for 'Data Analyst':
    {{
      "Senior Data Analyst": 0.6,
      "Business Intelligence Developer": 0.3,
      "Data Scientist": 0.1
    }}

    Now, generate the JSON for a starting role of '{role_title}':
    """
    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_text)
    except (json.JSONDecodeError, AttributeError, Exception) as e:
        print(f"Error generating career path for {role_title}: {e}")
        return None