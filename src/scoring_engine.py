import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sentence_transformers import SentenceTransformer, util
import os
import ast 

class SynapseScoringEngine:
    def __init__(self, data_path='data/processed/market_intelligence_db.csv', 
                 aspirational_data_path='data/processed/aspirational_roles.csv'):
        
        print("Initializing Synapse Scoring Engine...")
        
        try:
            df_manual = pd.read_csv(data_path)
            df_manual['tier'] = 'target' 
        except FileNotFoundError:
            raise Exception(f"Error: Main data file not found at {data_path}")
            
        try:
            if os.path.exists(aspirational_data_path):
                df_aspirational = pd.read_csv(aspirational_data_path)
                df_aspirational['tier'] = 'aspirational'
            else:
                df_aspirational = pd.DataFrame()
        except Exception as e:
            print(f"Warning: Could not load aspirational data. {e}")
            df_aspirational = pd.DataFrame()

        self.df = pd.concat([df_manual, df_aspirational], ignore_index=True)
        
        # Safely convert string-of-list to actual list
        self.df['skills_list'] = self.df['skills_list'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else []
        )
            
        print("Loading Sentence Transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully.")
        
        self._prepare_data()

    def _prepare_data(self):
        scaler = MinMaxScaler()
        
        self.df['norm_salary'] = scaler.fit_transform(self.df[['avg_salary_inr']].fillna(0))
        
        # CRITICAL CHANGE 2: Intelligently fill missing data for aspirational roles
        # This makes the synthetic data compatible with our scoring model
        self.df['role_volume'] = self.df.groupby('Standard_Title')['role_volume'].transform(lambda x: x.fillna(x.mean()))
        self.df['fgm_score'] = self.df.groupby('Standard_Title')['fgm_score'].transform(lambda x: x.fillna(x.mean()))
        
        log_volume = np.log(self.df['role_volume'].fillna(1).replace(0, 1))
        self.df['norm_cmp'] = scaler.fit_transform(log_volume.values.reshape(-1, 1))
        self.df['norm_fgm'] = scaler.fit_transform(self.df[['fgm_score']].fillna(0))

        weights_demand = {'cmp': 0.4, 'fgm': 0.6}
        self.df['final_demand_score'] = (weights_demand['cmp'] * self.df['norm_cmp']) + (weights_demand['fgm'] * self.df['norm_fgm'])
        print("Data preparation complete.")

    def _get_semantic_similarity(self, job_skills_text, user_embedding):
        if not job_skills_text: return 0
        job_embedding = self.model.encode(job_skills_text, convert_to_tensor=True)
        return util.pytorch_cos_sim(user_embedding, job_embedding).item()
        
    def get_tiered_recommendations(self, user_skills):
        if not user_skills: return {}

        user_embedding = self.model.encode(' '.join(user_skills), convert_to_tensor=True)
        
        # Create the user skills set once for efficiency
        user_skills_set = set(s.lower() for s in user_skills)

        # Ensure the skill_graph column is a dictionary
        self.df['skill_graph_eval'] = self.df['skill_graph'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('{') else {}
        )

        # Calculate the new hierarchical score
        self.df['skill_overlap_score'] = self.df['skill_graph_eval'].apply(
            lambda graph: self._calculate_hierarchical_skill_score(graph, user_skills_set)
        )

        master_weights = {'demand': 0.4, 'salary': 0.3, 'skill': 0.3}
        self.df['TrajectoryScore'] = (master_weights['demand'] * self.df['final_demand_score']) + \
                                     (master_weights['salary'] * self.df['norm_salary']) + \
                                     (master_weights['skill'] * self.df['skill_overlap_score'])
        
        # Step A: Find the best overall job to determine the top recommended ROLE
        top_job = self.df.loc[self.df['TrajectoryScore'].idxmax()]
        top_role_title = top_job['Standard_Title']

        # Step B: Filter for only jobs of that top role
        role_df = self.df[self.df['Standard_Title'] == top_role_title].copy()
        
        # Step C: Find the best example for each tier
        aspirational_tier = role_df[role_df['tier'] == 'aspirational'].nlargest(1, 'TrajectoryScore')
        target_tier = role_df[role_df['tier'] == 'target'].nlargest(1, 'TrajectoryScore')
        discovery_tier = role_df[role_df['tier'] == 'target'].nlargest(5, 'TrajectoryScore').tail(1)
        
        # Step D: Prepare the final structured output
        output = {
            "top_role_title": top_role_title,
            "your_skill_match_percent": round(top_job['skill_overlap_score'] * 100, 2),
            "market_demand_score": round(top_job['final_demand_score'] * 100, 2),
            "tiers": {
                "aspirational": aspirational_tier.to_dict(orient='records')[0] if not aspirational_tier.empty else None,
                "target": target_tier.to_dict(orient='records')[0] if not target_tier.empty else None,
                "discovery": discovery_tier.to_dict(orient='records')[0] if not discovery_tier.empty else None,
            }
        }
        return output

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
            "skills_to_develop": missing_skills[:5] 
        }
    
    def _calculate_hierarchical_skill_score(self, skill_graph, user_skills_set):
        """
        Calculates a weighted skill score based on the hierarchical skill graph.
        """
        if not skill_graph or not isinstance(skill_graph, dict):
            return 0

        # Define weights for different skill categories
        # These can be tuned for different job roles in the future
        category_weights = {
            "AI/ML Engineer": {
                "Programming Languages": 1.5,
                "Frameworks & Libraries": 1.5,
                "ML Frameworks": 2.2,
                "Databases": 1.0,
                "Cloud Platforms": 1.3,
                "Developer Tools": 1.0,
                "Key Concepts": 1.9,
                "Soft Skills": 0.6,
            },

            "App Developer": {
                "Programming Languages": 1.4,
                "Frameworks & Libraries": 1.8,
                "ML Frameworks": 0.8,
                "Databases": 1.2,
                "Cloud Platforms": 1.1,
                "Developer Tools": 1.3,
                "Key Concepts": 1.4,
                "Soft Skills": 0.6,
            },

            "Backend Developer": {
                "Programming Languages": 1.7,
                "Frameworks & Libraries": 1.5,
                "ML Frameworks": 0.7,
                "Databases": 1.6,
                "Cloud Platforms": 1.4,
                "Developer Tools": 1.2,
                "Key Concepts": 1.5,
                "Soft Skills": 0.5,
            },

            "Business Analyst": {
                "Programming Languages": 0.8,
                "Frameworks & Libraries": 0.7,
                "ML Frameworks": 0.5,
                "Databases": 1.4,
                "Cloud Platforms": 1.0,
                "Developer Tools": 0.8,
                "Key Concepts": 2.0,
                "Soft Skills": 1.5,
            },

            "CyberSecurity Analyst": {
                "Programming Languages": 1.2,
                "Frameworks & Libraries": 1.0,
                "ML Frameworks": 0.6,
                "Databases": 1.2,
                "Cloud Platforms": 1.5,
                "Developer Tools": 1.3,
                "Key Concepts": 2.1,
                "Soft Skills": 0.7,
            },

            "Data Analyst": {
                "Programming Languages": 1.3,
                "Frameworks & Libraries": 1.0,
                "ML Frameworks": 1.2,
                "Databases": 1.6,
                "Cloud Platforms": 1.0,
                "Developer Tools": 1.0,
                "Key Concepts": 1.8,
                "Soft Skills": 1.0,
            },

            "DevOps": {
                "Programming Languages": 1.2,
                "Frameworks & Libraries": 1.0,
                "ML Frameworks": 0.5,
                "Databases": 1.2,
                "Cloud Platforms": 2.0,
                "Developer Tools": 1.8,
                "Key Concepts": 1.5,
                "Soft Skills": 0.6,
            },

            "Frontend Developer": {
                "Programming Languages": 1.3,
                "Frameworks & Libraries": 2.0,
                "ML Frameworks": 0.5,
                "Databases": 1.0,
                "Cloud Platforms": 1.0,
                "Developer Tools": 1.2,
                "Key Concepts": 1.6,
                "Soft Skills": 0.7,
            },

            "FullStack Developer": {
                "Programming Languages": 1.6,
                "Frameworks & Libraries": 1.7,
                "ML Frameworks": 0.7,
                "Databases": 1.5,
                "Cloud Platforms": 1.4,
                "Developer Tools": 1.4,
                "Key Concepts": 1.6,
                "Soft Skills": 0.6,
            },

            "Network Engineer": {
                "Programming Languages": 1.0,
                "Frameworks & Libraries": 0.8,
                "ML Frameworks": 0.4,
                "Databases": 1.0,
                "Cloud Platforms": 1.5,
                "Developer Tools": 1.2,
                "Key Concepts": 2.0,
                "Soft Skills": 0.8,
            },

            "Product Engineer": {
                "Programming Languages": 1.3,
                "Frameworks & Libraries": 1.4,
                "ML Frameworks": 0.8,
                "Databases": 1.1,
                "Cloud Platforms": 1.2,
                "Developer Tools": 1.3,
                "Key Concepts": 1.9,
                "Soft Skills": 1.2,
            },

            "Software Developer": {
                "Programming Languages": 1.6,
                "Frameworks & Libraries": 1.5,
                "ML Frameworks": 0.7,
                "Databases": 1.3,
                "Cloud Platforms": 1.2,
                "Developer Tools": 1.3,
                "Key Concepts": 1.5,
                "Soft Skills": 0.6,
            },

            "Software Engineer": {
                "Programming Languages": 1.7,
                "Frameworks & Libraries": 1.6,
                "ML Frameworks": 0.9,
                "Databases": 1.4,
                "Cloud Platforms": 1.4,
                "Developer Tools": 1.4,
                "Key Concepts": 1.8,
                "Soft Skills": 0.8,
            },

            "Software Tester": {
                "Programming Languages": 1.0,
                "Frameworks & Libraries": 1.0,
                "ML Frameworks": 0.5,
                "Databases": 1.1,
                "Cloud Platforms": 1.0,
                "Developer Tools": 1.5,
                "Key Concepts": 1.6,
                "Soft Skills": 1.2,
            },

            "Technical Support": {
                "Programming Languages": 0.8,
                "Frameworks & Libraries": 0.7,
                "ML Frameworks": 0.4,
                "Databases": 1.0,
                "Cloud Platforms": 1.0,
                "Developer Tools": 1.0,
                "Key Concepts": 1.5,
                "Soft Skills": 1.5,
            }
        }

        
        total_score = 0
        total_possible_score = 0
        
        for category, skills in skill_graph.items():
            weight = category_weights.get(category, 1.0) 
            
            job_skills_in_category = set(s.lower() for s in skills)
            match_count = len(job_skills_in_category.intersection(user_skills_set))
            
            total_score += match_count * weight
            total_possible_score += len(job_skills_in_category) * weight
            
        if total_possible_score == 0:
            return 0
            
        return total_score / total_possible_score

# --- Example Usage ---
if __name__ == '__main__':
    engine = SynapseScoringEngine()
    
    my_skills = ["Python", "Deep Learning", "NLP", "Git", "Object Oriented Programming", "Communication"]
    
    # 1. Get General Recommendations
    recommendations = engine.get_tiered_recommendations(user_skills=my_skills)
    import json
    print("\n Tiered Career Recommendation")
    print(json.dumps(recommendations, indent=2))

    # 2. Perform a Specific Gap Analysis
    gap_results = engine.perform_gap_analysis(
        user_skills=my_skills,
        dream_role="AI/ML Engineer",
        dream_company="Google"
    )
    print("\n Gap Analysis for Your Dream Role ")
    print(gap_results)