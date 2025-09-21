import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sentence_transformers import SentenceTransformer, util, CrossEncoder
import os
import ast
import json


class SynapseScoringEngine:
    def __init__(self, data_path='data/processed/market_intelligence_db.csv',
                 aspirational_data_path='data/processed/aspirational_roles.csv',
                 career_path_model_path='data/processed/career_path_model.json'):

        print("Initializing Synapse Scoring Engine...")

        try:
            df_manual = pd.read_csv(data_path)
            df_manual['tier'] = 'target'
        except FileNotFoundError:
            raise Exception(f"Error: Main data file not found at {data_path}")

        try:
            if os.path.exists(aspirational_data_path):
                self.df_aspirational = pd.read_csv(aspirational_data_path)
                self.df_aspirational['tier'] = 'aspirational'
            else:
                self.df_aspirational = pd.DataFrame()
        except Exception as e:
            print(f"Warning: Could not load aspirational data. {e}")
            self.df_aspirational = pd.DataFrame()

        # Merge target + aspirational
        self.df = pd.concat([df_manual, self.df_aspirational], ignore_index=True)

        # Safely convert string-of-list and dict columns
        self.df['skills_list'] = self.df['skills_list'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else []
        )
        self.df['skill_graph'] = self.df['skill_graph'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('{') else {}
        )

        # Career path model
        try:
            with open(career_path_model_path, 'r') as f:
                self.career_path_model = json.load(f)
            print("Career path model loaded successfully.")
        except FileNotFoundError:
            print(f"Warning: Career path model not found at {career_path_model_path}. Proceeding without it.")
            self.career_path_model = {}

        # Load models
        print("Loading Sentence Transformer (Bi-Encoder) model...")
        self.bi_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        print("Bi-Encoder loaded.")

        print("Loading Cross-Encoder model...")
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        print("Cross-Encoder loaded.")

        self._prepare_data()

    def _prepare_data(self):
        scaler = MinMaxScaler()

        self.df['norm_salary'] = scaler.fit_transform(self.df[['avg_salary_inr']].fillna(0))
        self.df['role_volume'] = self.df.groupby('Standard_Title')['role_volume'].transform(lambda x: x.fillna(x.mean()))
        self.df['fgm_score'] = self.df.groupby('Standard_Title')['fgm_score'].transform(lambda x: x.fillna(x.mean()))

        log_volume = np.log(self.df['role_volume'].fillna(1).replace(0, 1))
        self.df['norm_cmp'] = scaler.fit_transform(log_volume.values.reshape(-1, 1))
        self.df['norm_fgm'] = scaler.fit_transform(self.df[['fgm_score']].fillna(0))

        weights_demand = {'cmp': 0.4, 'fgm': 0.6}
        self.df['final_demand_score'] = (
            (weights_demand['cmp'] * self.df['norm_cmp']) +
            (weights_demand['fgm'] * self.df['norm_fgm'])
        )
        print("Data preparation complete.")

    def _get_semantic_similarity(self, job_skills_text, user_embedding):
        if not job_skills_text:
            return 0.0
        job_embedding = self.bi_encoder.encode(job_skills_text, convert_to_tensor=True)
        return float(util.pytorch_cos_sim(user_embedding, job_embedding).item())

    def get_tiered_recommendations(self, user_skills):
        if not user_skills:
            return {}

        # Stage 1: Fast search
        user_skills_set = set(s.lower() for s in user_skills)
        self.df['skill_overlap_score'] = self.df['skill_graph'].apply(
            lambda graph: self._calculate_hierarchical_skill_score(graph, user_skills_set)
        )

        master_weights = {'demand': 0.4, 'salary': 0.3, 'skill': 0.3}
        self.df['InitialTrajectoryScore'] = (
            (master_weights['demand'] * self.df['final_demand_score']) +
            (master_weights['salary'] * self.df['norm_salary']) +
            (master_weights['skill'] * self.df['skill_overlap_score'])
        )

        top_candidates = self.df.nlargest(20, 'InitialTrajectoryScore').copy()

        # Stage 2: Re-rank with cross-encoder
        user_skills_text = ' '.join(user_skills)
        job_skills_texts = top_candidates['skills_list'].apply(lambda skills: ' '.join(skills))
        sentence_pairs = [[user_skills_text, job_text] for job_text in job_skills_texts]

        print(f"Re-ranking top {len(sentence_pairs)} candidates with Cross-Encoder...")
        cross_encoder_scores = self.cross_encoder.predict(sentence_pairs)

        # Normalize cross-encoder scores (0–1)
        cross_encoder_scores = np.clip(cross_encoder_scores, 0, 1)
        top_candidates['skill_overlap_score'] = cross_encoder_scores

        top_candidates['TrajectoryScore'] = (
            (master_weights['demand'] * top_candidates['final_demand_score']) +
            (master_weights['salary'] * top_candidates['norm_salary']) +
            (master_weights['skill'] * top_candidates['skill_overlap_score'])
        )

        # Pick best role
        top_job = top_candidates.loc[top_candidates['TrajectoryScore'].idxmax()]
        top_role_title = str(top_job['Standard_Title'])

        role_df = top_candidates[top_candidates['Standard_Title'] == top_role_title]

        aspirational_tier = role_df[role_df['tier'] == 'aspirational'].nlargest(1, 'TrajectoryScore')
        target_tier = role_df[role_df['tier'] == 'target'].nlargest(1, 'TrajectoryScore')
        discovery_tier = role_df[role_df['tier'] == 'target'].nlargest(5, 'TrajectoryScore').tail(1)

        next_probable_steps = self.career_path_model.get(top_role_title, None)

        output = {
            "top_role_title": top_role_title,
            "your_skill_match_percent": round(float(top_job['skill_overlap_score']) * 100, 2),
            "market_demand_score": round(float(top_job['final_demand_score']) * 100, 2),
            "next_probable_steps": next_probable_steps,
            "tiers": {
                "aspirational": aspirational_tier.to_dict(orient='records')[0] if not aspirational_tier.empty else None,
                "target": target_tier.to_dict(orient='records')[0] if not target_tier.empty else None,
                "discovery": discovery_tier.to_dict(orient='records')[0] if not discovery_tier.empty else None,
            }
        }
        return output

    def perform_gap_analysis(self, user_skills, dream_role, dream_company):
        """
        Performs a skill gap analysis for a user's dream role and company.
        Falls back to role-only matching if company data is unavailable or no exact match is found.
        """
        # Detect company column
        company_col = None
        for col in self.df.columns:
            if col.lower() in ["companyname", "company", "organization", "org"]:
                company_col = col
                break

        # Role + company
        if company_col and dream_company:
            target_role = self.df[
                (self.df["Standard_Title"].str.lower() == dream_role.lower()) &
                (self.df[company_col].str.lower() == dream_company.lower())
            ]
        else:
            target_role = pd.DataFrame()

        # Role only fallback
        if target_role.empty:
            target_role = self.df[self.df["Standard_Title"].str.lower() == dream_role.lower()]

        if target_role.empty:
            return {
                "error": f"Role '{dream_role}'" +
                         (f" at '{dream_company}'" if dream_company else "") +
                         " not found in our database."
            }

        target_skills = target_role.iloc[0]['skills_list']

        user_embedding = self.bi_encoder.encode(' '.join(user_skills), convert_to_tensor=True)
        match_score = self._get_semantic_similarity(' '.join(target_skills), user_embedding)

        user_skills_set = set(s.lower() for s in user_skills)
        target_skills_set = set(s.lower() for s in target_skills)
        missing_skills = list(target_skills_set - user_skills_set)

        return {
            "dream_role": f"{dream_role}" + (f" at {dream_company}" if dream_company else ""),
            "match_score_percent": round(float(match_score) * 100, 2),
            "skills_to_develop": missing_skills[:5]
        }

    def _calculate_hierarchical_skill_score(self, skill_graph, user_skills_set):
        if not skill_graph or not isinstance(skill_graph, dict):
            return 0.0

        # Example category weights (expand as needed)
        category_weights = {
            "Programming Languages": 1.5,
            "Frameworks & Libraries": 1.3,
            "Databases": 1.2,
            "Cloud Platforms": 1.2,
            "Developer Tools": 1.0,
            "Key Concepts": 1.5,
            "Soft Skills": 0.6,
        }

        total_score = 0.0
        total_possible_score = 0.0

        for category, skills in skill_graph.items():
            weight = category_weights.get(category, 1.0)
            job_skills_in_category = set(s.lower() for s in skills)
            match_count = len(job_skills_in_category.intersection(user_skills_set))

            total_score += match_count * weight
            total_possible_score += len(job_skills_in_category) * weight

        if total_possible_score == 0:
            return 0.0
        return total_score / total_possible_score


# --- Example Usage ---
if __name__ == '__main__':
    engine = SynapseScoringEngine()

    my_skills = ["Python", "Deep Learning", "NLP", "Git", "Object Oriented Programming", "Communication"]

    # Recommendations
    recommendations = engine.get_tiered_recommendations(user_skills=my_skills)
    print("\nTiered Career Recommendation")
    print(json.dumps(recommendations, indent=2))

    # Gap Analysis
    gap_results = engine.perform_gap_analysis(
        user_skills=my_skills,
        dream_role="AI/ML Engineer",
        dream_company="Google"
    )
    print("\nGap Analysis for Your Dream Role")
    print(gap_results)
