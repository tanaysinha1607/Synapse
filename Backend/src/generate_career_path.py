import pandas as pd
import json
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from gemini_utils import generate_career_path_probabilities

# Setup Gemini 
load_dotenv(dotenv_path='.env')
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in ../.env file.")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Main Logic
def build_career_path_model():

    data_path =  r"D:\Desktop Data\ML\Projects\Synapse\data\processed\market_intelligence_db.csv"
    df = pd.read_csv(data_path)
    unique_roles = df['Standard_Title'].unique()
    
    career_path_model = {}
    
    for role in unique_roles:
        print(f"Generating career path for: {role}...")
        probabilities = generate_career_path_probabilities(role, model)
        
        if probabilities:
            career_path_model[role] = probabilities
        
        time.sleep(7) # Rate limiting
        
    output_path = r"D:\Desktop Data\ML\Projects\Synapse\data\processed\career_path_model.json"
    with open(output_path, 'w') as f:
        json.dump(career_path_model, f, indent=2)
        
    print(f"\nCareer path model successfully created at {output_path}")

if __name__ == '__main__':
    build_career_path_model()