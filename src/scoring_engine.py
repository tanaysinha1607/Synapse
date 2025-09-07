import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sentence_transformers import SentenceTransformer, util
import os

class SynapseScoringEngine:
    def __init__(self, data_path='data/processed/market_intelligence_db.csv', 
                 aspirational_data_path='data/processed/aspirational_roles.csv'):
        
        # Initializes the engine by loading the datasets and the AI model.
        
        print("Initializing Synapse Scoring Engine...")
        
        # --- Load Datasets ---
        try:
            self.df = pd.read_csv(data_path)
        except FileNotFoundError:
            raise Exception(f"Error: Main data file not found at {data_path}")
            
        try:
            if os.path.exists(aspirational_data_path):
                self.df_aspirational = pd.read_csv(aspirational_data_path)
            else:
                self.df_aspirational = pd.DataFrame() # Create empty if not found
        except Exception as e:
            print(f"Warning: Could not load aspirational data. {e}")
            self.df_aspirational = pd.DataFrame()
            
        # --- Load AI Model (ONCE) ---
        print("Loading Sentence Transformer model")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully.")
        
        # --- Pre-calculate user-independent scores ---
        self._prepare_data()
        print("Engine ready.")

    def _prepare_data(self):
        # Pre-calculates all scores that do not depend on user input.
        scaler = MinMaxScaler()
        
        # 1. Normalize Salary
        self.df['norm_salary'] = scaler.fit_transform(self.df[['avg_salary_inr']].fillna(0))
        
        # 2. Calculate and Normalize Demand Scores (CMP & FGM)
        log_volume = np.log(self.df['role_volume'].replace(0, 1))
        self.df['norm_cmp'] = scaler.fit_transform(log_volume.values.reshape(-1, 1))
        self.df['norm_fgm'] = scaler.fit_transform(self.df[['fgm_score']].fillna(0))
        
        # 3. Calculate Final Demand Score
        weights_demand = {'cmp': 0.4, 'fgm': 0.6}
        self.df['final_demand_score'] = (weights_demand['cmp'] * self.df['norm_cmp']) + \
                                      (weights_demand['fgm'] * self.df['norm_fgm'])
        
        # 4. Ensure skills_list is an actual list (not a string)
        # This prevents errors if the CSV is re-loaded
        self.df['skills_list'] = self.df['skills_list'].apply(
            lambda x: eval(x) if isinstance(x, str) else []
        )
        if not self.df_aspirational.empty:
            self.df_aspirational['skills_list'] = self.df_aspirational['skills_list'].apply(
                lambda x: eval(x) if isinstance(x, str) else []
            )

    def _get_semantic_similarity(self, job_skills_text, user_embedding):
        if not job_skills_text:
            return 0
        job_embedding = self.model.encode(job_skills_text, convert_to_tensor=True)
        cosine_score = util.pytorch_cos_sim(user_embedding, job_embedding)
        return cosine_score.item()

    def get_recommendations(self, user_skills, top_n=5):
        # Calculates general career recommendations based on user skills.
        if not user_skills:
            return pd.DataFrame()

        # Create a copy to avoid modifying the original dataframe in place
        df_scored = self.df.copy()

        user_embedding = self.model.encode(' '.join(user_skills), convert_to_tensor=True)
        df_scored['skill_overlap_score'] = df_scored['skills_list'].apply(
            lambda skills: self._get_semantic_similarity(' '.join(skills), user_embedding)
        )

        master_weights = {'demand': 0.4, 'salary': 0.3, 'skill': 0.3}
        df_scored['TrajectoryScore'] = (master_weights['demand'] * df_scored['final_demand_score']) + \
                                      (master_weights['salary'] * df_scored['norm_salary']) + \
                                      (master_weights['skill'] * df_scored['skill_overlap_score'])
        
        recommendations = df_scored.sort_values(by='TrajectoryScore', ascending=False)
        return recommendations.head(top_n)

    def perform_gap_analysis(self, user_skills, dream_role, dream_company):
        # Performs a skill gap analysis for a user's dream role and company.
        target_df = pd.concat([self.df, self.df_aspirational])
        target_role = target_df[
            (target_df['Standard_Title'].str.lower() == dream_role.lower()) & 
            (target_df['CompanyName'].str.lower() == dream_company.lower())
        ]

        if target_role.empty:
            return {"error": f"Role '{dream_role}' at '{dream_company}' not found in our database."}

        target_skills = target_role.iloc[0]['skills_list']
        
        user_embedding = self.model.encode(' '.join(user_skills), convert_to_tensor=True)
        match_score = self._get_semantic_similarity(' '.join(target_skills), user_embedding)
        
        user_skills_set = set(s.lower() for s in user_skills)
        target_skills_set = set(s.lower() for s in target_skills)
        missing_skills = list(target_skills_set - user_skills_set)
        
        return {
            "dream_role": f"{dream_role} at {dream_company}",
            "match_score_percent": round(match_score * 100, 2),
            "skills_to_develop": missing_skills[:5] # Show top 5 for brevity
        }

# --- Example Usage ---
if __name__ == '__main__':
    engine = SynapseScoringEngine()
    
    my_skills = ["Python", "Deep Learning", "NLP", "Git", "Object Oriented Programming", "Communication"]
    
    # 1. Get General Recommendations
    top_jobs = engine.get_recommendations(user_skills=my_skills)
    print("\nTop 5 General Career Recommendations ")
    if not top_jobs.empty:
        print(top_jobs[[
            'Standard_Title', 'CompanyName', 'TrajectoryScore'
        ]].head())
    else:
        print("No recommendations found.")

    # 2. Perform a Specific Gap Analysis
    gap_results = engine.perform_gap_analysis(
        user_skills=my_skills,
        dream_role="AI/ML Engineer",
        dream_company="Google"
    )
    print("\n Gap Analysis for Your Dream Role ")
    print(gap_results)