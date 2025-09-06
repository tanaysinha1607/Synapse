import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sentence_transformers import SentenceTransformer, util
from data_processing import process_raw_data

def calculate_scores(processed_df, user_skills):
    """
    Takes the processed DataFrame and a user's skills to calculate the final TrajectoryScore.
    """
    df = processed_df.copy()
    
    scaler = MinMaxScaler()
    df['norm_salary'] = scaler.fit_transform(df[['avg_salary_inr']].fillna(0))
    
    log_volume = np.log(df['role_volume'].replace(0, 1))
    scaler_cmp = MinMaxScaler(feature_range=(1, 5))
    df['cmp_score'] = scaler_cmp.fit_transform(log_volume.values.reshape(-1, 1))
    df['norm_cmp'] = scaler.fit_transform(df[['cmp_score']].fillna(0))
    
    df['norm_fgm'] = scaler.fit_transform(df[['fgm_score']].fillna(0))

    weights_demand = {'cmp': 0.4, 'fgm': 0.6}
    df['final_demand_score'] = (weights_demand['cmp'] * df['norm_cmp']) + \
                               (weights_demand['fgm'] * df['norm_fgm'])

    model = SentenceTransformer('all-MiniLM-L6-v2')
    user_skills_embedding = model.encode(' '.join(user_skills), convert_to_tensor=True)

    def get_semantic_similarity(job_skills_list):
        if not job_skills_list or not isinstance(job_skills_list, list):
            return 0
        job_skills_text = ' '.join(job_skills_list)
        job_skills_embedding = model.encode(job_skills_text, convert_to_tensor=True)
        cosine_score = util.pytorch_cos_sim(user_skills_embedding, job_skills_embedding)
        return cosine_score.item()

    df['skill_overlap_score'] = df['skills_list'].apply(get_semantic_similarity)

    master_weights = {'demand': 0.4, 'salary': 0.3, 'skill': 0.3}
    df['TrajectoryScore'] = (master_weights['demand'] * df['final_demand_score']) + \
                            (master_weights['salary'] * df['norm_salary']) + \
                            (master_weights['skill'] * df['skill_overlap_score'])
    
    return df.sort_values(by='TrajectoryScore', ascending=False)