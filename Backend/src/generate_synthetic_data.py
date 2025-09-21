import google.generativeai as genai
import pandas as pd
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Configure your Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key= api_key)

model = genai.GenerativeModel('gemini-1.5-flash-latest')

ASPIRATIONAL_ROLES = [
    {"company": "Google", "role": "Software Engineer"},
    {"company": "Microsoft", "role": "Software Engineer"},
    {"company": "Apple", "role": "AI/ML Engineer"},
    {"company": "NVIDIA", "role": "AI/ML Engineer"},
    {"company": "Meta", "role": "App Developer"},
    {"company": "Spotify", "role": "App Developer"},
    {"company": "Amazon", "role": "Backend Developer"},
    {"company": "Netflix", "role": "Backend Developer"},
    {"company": "McKinsey & Company", "role": "Business Analyst"},
    {"company": "Deloitte", "role": "Business Analyst"},
    {"company": "CrowdStrike", "role": "CyberSecurity Analyst"},
    {"company": "Palo Alto Networks", "role": "CyberSecurity Analyst"},
    {"company": "IBM", "role": "Data Analyst"},
    {"company": "Airbnb", "role": "Data Analyst"},
    {"company": "Red Hat", "role": "DevOps"},
    {"company": "Atlassian", "role": "DevOps"},
    {"company": "Shopify", "role": "Frontend Developer"},
    {"company": "Adobe", "role": "Frontend Developer"},
    {"company": "Uber", "role": "FullStack Developer"},
    {"company": "Stripe", "role": "FullStack Developer"},
    {"company": "Cisco", "role": "Network Engineer"},
    {"company": "Juniper Networks", "role": "Network Engineer"},
    {"company": "Tesla", "role": "Product Engineer"},
    {"company": "SpaceX", "role": "Product Engineer"},
    {"company": "Oracle", "role": "Software Developer"},
    {"company": "SAP", "role": "Software Developer"},
    {"company": "LinkedIn", "role": "Software Engineer"},
    {"company": "Bloomberg", "role": "Software Engineer"},
    {"company": "Infosys", "role": "Software Tester"},
    {"company": "Cognizant", "role": "Software Tester"},
    {"company": "Dell", "role": "Technical Support"},
    {"company": "HP", "role": "Technical Support"}
]


def generate_synthetic_profile(company, role, model):
    prompt = f"""
    Act as a career data analyst for the Indian market.
    Provide a realistic profile for an entry-level (0-2 years experience) '{role}' at '{company}' in India.
    Your output MUST be a valid JSON object with the following keys and value types:
    - "Standard_Title": string (e.g., "Software Engineer")
    - "CompanyName": string (e.g., "{company}")
    - "avg_salary_inr": integer (a realistic estimated average annual salary in INR)
    - "skills_list": list of 10-15 essential technical and soft skills as strings.
    
    Example for "Product Manager" at "Microsoft":
    {{
      "Standard_Title": "Product Manager",
      "CompanyName": "Microsoft",
      "avg_salary_inr": 2500000,
      "skills_list": ["Product Strategy", "User Research", "Agile Methodologies", "Data Analysis", "SQL", "Public Speaking", "Stakeholder Management"]
    }}

    Now, generate the JSON for '{role}' at '{company}':
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean the response text to remove markdown formatting if present
        cleaned_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_text)
    except (json.JSONDecodeError, AttributeError, Exception) as e:
        print(f"Error parsing JSON for {company} {role}: {e}")
        print(f"--- Raw Response Text ---\n{response.text}\n")
        return None

# --- Main script ---
if __name__ == '__main__':
    all_profiles = []
    
    for item in ASPIRATIONAL_ROLES:
        print(f"Generating profile for {item['role']} at {item['company']}...")
        profile = generate_synthetic_profile(item['company'], item['role'], model)
        if profile:
            all_profiles.append(profile)
        time.sleep(10)
            
    df_synthetic = pd.DataFrame(all_profiles)
    
    output_path = 'data/processed/aspirational_roles.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_synthetic.to_csv(output_path, index=False)
    
    print(f"\nSynthetic dataset created and saved to {output_path}")
    print(df_synthetic.head())