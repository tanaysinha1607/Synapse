import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv

# --- Project Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)

# --- Load .env File ---
ENV_PATH = os.path.join(BACKEND_DIR, '.env')
load_dotenv(dotenv_path=ENV_PATH) 

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(f"GEMINI_API_KEY not found. Looked for .env file at: {ENV_PATH}")
genai.configure(api_key=api_key)

print("--- Checking for available Gemini models... ---")

try:
    # List all models
    models = genai.list_models()
    
    print("\nFound the following models that support 'generateContent':\n")
    
    found_model = False
    for m in models:
        # We only care about models that can be used for our text-gen task
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model name: {m.name}")
            found_model = True

    if not found_model:
        print("Could not find any models that support 'generateContent'.")
        print("This might be an issue with your API key permissions or project setup.")

except Exception as e:
    print(f"An error occurred while trying to list models: {e}")
    print("Please double-check your API key and that the Generative AI API is enabled in your Google Cloud project.")

print("\n--- Check complete ---")