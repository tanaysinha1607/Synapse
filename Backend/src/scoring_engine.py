import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sentence_transformers import SentenceTransformer, util, CrossEncoder
import os
import ast 
import json

# Domain mapping for Q9 (work_energy)
DOMAIN_MAP = {
    'building_products': ['Software Engineer', 'App Developer', 'Frontend Developer', 'Backend Developer', 'FullStack Developer', 'Product Engineer'],
    'analyzing_data': ['Data Analyst', 'Business Analyst', 'AI/ML Engineer'],
    'optimizing_systems': ['AI/ML Engineer', 'DevOps', 'Network Engineer', 'Software Tester'],
    'collaborating': ['Business Analyst', 'Product Engineer', 'Technical Support']
}

class SynapseScoringEngine:
    def __init__(self, data_path='data/processed/market_intelligence_db.csv', 
                 aspirational_data_path='data/processed/aspirational_roles.csv',
                 career_path_model_path='data/processed/career_path_model.json'):
        
        print("Initializing Synapse Scoring Engine...")
        
        # --- 1. Load Datasets ---
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

        self.master_df = pd.concat([df_manual, df_aspirational], ignore_index=True)
        
        # --- 2. Pre-parse all data on init ---
        self.master_df['skills_list'] = self.master_df['skills_list'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else []
        )
        self.master_df['skill_graph'] = self.master_df['skill_graph'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('{') else {}
        )
            
        # --- 3. Load Career Path Model ---
        try:
            with open(career_path_model_path, 'r') as f:
                self.career_path_model = json.load(f)
            print("Career path model loaded.")
        except FileNotFoundError:
            print(f"Warning: Career path model not found at {career_path_model_path}. Proceeding without it.")
            self.career_path_model = {}

        # --- 4. Load AI Models ---
        print("Loading Sentence Transformer (Bi-Encoder) model...")
        self.bi_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        print("Loading Cross-Encoder model...")
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        self._prepare_data()
        print("Engine ready.")

    def _prepare_data(self):
        # (This function is unchanged)
        scaler = MinMaxScaler()
        self.master_df['norm_salary'] = scaler.fit_transform(self.master_df[['avg_salary_inr']].fillna(0))
        self.master_df['role_volume'] = self.master_df.groupby('Standard_Title')['role_volume'].transform(lambda x: x.fillna(x.mean()))
        self.master_df['fgm_score'] = self.master_df.groupby('Standard_Title')['fgm_score'].transform(lambda x: x.fillna(x.mean()))
        log_volume = np.log(self.master_df['role_volume'].fillna(1).replace(0, 1))
        self.master_df['norm_cmp'] = scaler.fit_transform(log_volume.values.reshape(-1, 1))
        self.master_df['norm_fgm'] = scaler.fit_transform(self.master_df[['fgm_score']].fillna(0))
        weights_demand = {'cmp': 0.4, 'fgm': 0.6}
        self.master_df['final_demand_score'] = (weights_demand['cmp'] * self.master_df['norm_cmp']) + (weights_demand['fgm'] * self.master_df['norm_fgm'])
        print("Data preparation complete.")

    ### NEW: Sigmoid function to normalize scores
    def _sigmoid(self, x):
        """Squashes any number to a 0-1 range."""
        return 1 / (1 + np.exp(-x))

    def _get_dynamic_weights(self, quiz_data):
        # (This function is unchanged)
        motivator = quiz_data.get('primary_motivator', 'learning')
        
        if motivator == 'salary':
            return {'demand': 0.2, 'salary': 0.5, 'skill': 0.2, 'experience': 0.1}
        elif motivator == 'learning':
            return {'demand': 0.2, 'salary': 0.1, 'skill': 0.4, 'experience': 0.3}
        elif motivator == 'prestige':
             return {'demand': 0.4, 'salary': 0.2, 'skill': 0.2, 'experience': 0.2}
        else:
            return {'demand': 0.3, 'salary': 0.2, 'skill': 0.3, 'experience': 0.2}

    def _get_skill_gap(self, user_skills, target_skills):
        # (This function is unchanged)
        user_skills_set = set(s.lower() for s in user_skills)
        target_skills_set = set(s.lower() for s in target_skills)
        missing_skills = list(target_skills_set - user_skills_set)
        return missing_skills

    def _calculate_hierarchical_skill_score(self, skill_graph, user_skills_set):
        # (This function is unchanged)
        if not skill_graph or not isinstance(skill_graph, dict): return 0
        category_weights = {"Programming Languages": 1.8, "Key Concepts": 1.8, "Frameworks & Libraries": 1.5, "ML Frameworks": 2.0, "Databases": 1.2, "Cloud Platforms": 1.2, "Developer Tools": 1.0, "Soft Skills": 0.5}
        total_score, total_possible_score = 0, 0
        for category, skills in skill_graph.items():
            weight = category_weights.get(category, 1.0)
            job_skills_in_cat = set(s.lower() for s in skills)
            match_count = len(job_skills_in_cat.intersection(user_skills_set))
            total_score += match_count * weight
            total_possible_score += len(job_skills_in_cat) * weight
        return total_score / total_possible_score if total_possible_score > 0 else 0
        
    def get_tiered_recommendations(self, user_skills, user_experience_summary, user_certifications, quiz_data):
        # (Logic from Step 1-5 is unchanged)
        
        # 1. Create a working copy
        df = self.master_df.copy()

        # 2. Apply Hard Filters
        min_salary = quiz_data.get('min_salary_inr', 0)
        if min_salary > 0:
            df = df[df['avg_salary_inr'] >= min_salary]
        
        work_energy = quiz_data.get('work_energy')
        if work_energy in DOMAIN_MAP:
            allowed_roles = DOMAIN_MAP[work_energy]
            df = df[df['Standard_Title'].isin(allowed_roles)]

        if df.empty:
            return {"error": "No jobs match your specific criteria. Try broadening your quiz answers."}

        # 3. Get Dynamic Weights
        master_weights = self._get_dynamic_weights(quiz_data)

        # 4. STAGE 1: FIND
        user_skills_set = set(s.lower() for s in user_skills)
        df['skill_overlap_score_initial'] = df['skill_graph'].apply(
            lambda graph: self._calculate_hierarchical_skill_score(graph, user_skills_set)
        )
        w_d, w_s, w_sk = master_weights['demand'], master_weights['salary'], master_weights['skill']
        norm_factor = w_d + w_s + w_sk
        df['InitialTrajectoryScore'] = ((w_d * df['final_demand_score']) +
                                       (w_s * df['norm_salary']) +
                                       (w_sk * df['skill_overlap_score_initial'])) / (norm_factor if norm_factor > 0 else 1)

        # 5. Apply Score Biases
        goal = quiz_data.get('career_goal', 'exploring')
        work_env = quiz_data.get('work_environment')
        bias_boost = 0.2
        df['BiasedScore'] = df['InitialTrajectoryScore']
        if goal == 'top_company' or work_env == 'structured':
            df['BiasedScore'] += (df['tier'] == 'aspirational') * bias_boost
        if goal == 'startup' or work_env == 'startup':
            df['BiasedScore'] += (df['norm_fgm'] > 0.7) * bias_boost
             
        top_candidates = df.nlargest(30, 'BiasedScore').copy()
        
        if top_candidates.empty:
             return {"error": "No top candidates found after initial scoring."}

        # 6. STAGE 2: REFINE
        user_skills_text = ' '.join(user_skills)
        job_skills_texts = top_candidates['skills_list'].apply(lambda skills: ' '.join(skills))
        skill_sentence_pairs = [[user_skills_text, job_text] for job_text in job_skills_texts]
        
        ### MODIFIED: Apply sigmoid to normalize the score
        cross_encoder_skill_scores = self.cross_encoder.predict(skill_sentence_pairs, show_progress_bar=False)
        top_candidates['skill_overlap_score'] = self._sigmoid(cross_encoder_skill_scores)
        
        user_experience_text = " ".join(user_experience_summary) + " " + " ".join(user_certifications)
        if not user_experience_text.strip():
            top_candidates['experience_score'] = 0.0
        else:
            job_context_texts = top_candidates.apply(
                lambda row: row['Standard_Title'] + " " + " ".join(row['skills_list']),
                axis=1
            )
            exp_sentence_pairs = [[user_experience_text, job_text] for job_text in job_context_texts]
            ### MODIFIED: Apply sigmoid to normalize the score
            cross_encoder_exp_scores = self.cross_encoder.predict(exp_sentence_pairs, show_progress_bar=False)
            top_candidates['experience_score'] = self._sigmoid(cross_encoder_exp_scores)


        # 7. Final Trajectory Score Calculation
        w_d, w_s, w_sk, w_exp = master_weights['demand'], master_weights['salary'], master_weights['skill'], master_weights['experience']
        top_candidates['TrajectoryScore'] = (w_d * top_candidates['final_demand_score']) + \
                                            (w_s * top_candidates['norm_salary']) + \
                                            (w_sk * top_candidates['skill_overlap_score']) + \
                                            (w_exp * top_candidates['experience_score'])
        
        # 8. Final Selection
        top_job = top_candidates.loc[top_candidates['TrajectoryScore'].idxmax()]
        top_role_title = top_job['Standard_Title']
        top_job_skills = self.master_df.loc[top_job.name]['skills_list']
        skill_gap = self._get_skill_gap(user_skills, top_job_skills)
        role_df = top_candidates[top_candidates['Standard_Title'] == top_role_title]
        target_tier = role_df[role_df['tier'] == 'target'].nlargest(1, 'TrajectoryScore')

        # 9. Construct Final Output JSON (Casting all numbers)
        output = {
            "top_recommendation": {
                "job_title": str(top_role_title),
                "company_name": str(target_tier.iloc[0]['CompanyName'] if not target_tier.empty else top_job['CompanyName']),
                "location": str(target_tier.iloc[0]['Location'] if not target_tier.empty else top_job['Location']),
                "avg_salary_inr": int(target_tier.iloc[0]['avg_salary_inr']) if not target_tier.empty else int(top_job['avg_salary_inr']),
                "skill_match_percent": float(round(top_job['skill_overlap_score'] * 100, 2)),
                "probabilistic_next_steps": self.career_path_model.get(top_role_title, None)
            },
            
            "roadmap_inputs": {
                "target_job_title": str(top_role_title),
                "skill_gap": skill_gap,
                "user_context": {
                    "hours_per_week": quiz_data.get('hours_per_week', '4-6'),
                    "learning_style": quiz_data.get('learning_style', 'projects'),
                    "skill_confidence": quiz_data.get('skill_confidence', 'intermediate'),
                    "future_ambition": quiz_data.get('future_ambition', 'technical_mastery')
                }
            }
        }
        return output

    def perform_gap_analysis(self, user_skills, dream_role, dream_company):
        target_df = self.master_df[
            (self.master_df['Standard_Title'].str.lower() == dream_role.lower())
        ]
        if dream_company:
             target_df = target_df[target_df['CompanyName'].str.lower() == dream_company.lower()]

        if target_df.empty:
            return {"error": f"Role '{dream_role}' at '{dream_company}' not found."}

        target_role = target_df.iloc[0]
        target_skills = target_role['skills_list']
        
        skill_gap = self._get_skill_gap(user_skills, target_skills)
        
        user_skills_text = ' '.join(user_skills)
        target_skills_text = ' '.join(target_skills)
        
        ### MODIFIED: Apply sigmoid to normalize the score
        raw_match_score = self.cross_encoder.predict([[user_skills_text, target_skills_text]])[0]
        normalized_score = self._sigmoid(raw_match_score)

        return {
            "dream_role": f"{target_role['Standard_Title']} at {target_role['CompanyName']}",
            "match_score_percent": float(round(float(normalized_score) * 100, 2)),
            "skills_to_develop": skill_gap
        }