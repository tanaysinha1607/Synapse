import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy import stats

def clean_salary(salary_range):

    if not isinstance(salary_range, str):
        return np.nan
    try:
        low, high = [float(s.strip()) for s in salary_range.split('-')]
        return (low + high) / 2 * 100000
    except (ValueError, AttributeError):
        return np.nan

def parse_skills(skills_text):

    if not isinstance(skills_text, str):
        return []
    cleaned_text = skills_text.replace('\n', ' ').strip()
    skills_list = [skill.strip() for skill in cleaned_text.split(',')]
    return skills_list

def standardize_date(date_str):

    if not isinstance(date_str, str):
        return pd.NaT
    
    today = datetime.now()
    date_str = date_str.lower()
    
    try:
        num, unit = date_str.split()[:2]
        num = int(num)
        if 'day' in unit:
            return today - timedelta(days=num)
        elif 'week' in unit:
            return today - timedelta(weeks=num)
        elif 'month' in unit:
            return today - timedelta(days=num * 30) # Approximation
        else:
            return pd.NaT
    except (ValueError, IndexError):
        return pd.NaT

def get_trend_slope(csv_file_path):

    try:
        trends_df = pd.read_csv(csv_file_path, skiprows=2)
        trends_df.columns = ['Month', 'Interest']
        trends_df['Interest'] = pd.to_numeric(trends_df['Interest'], errors='coerce').fillna(0)
        trends_df['Time_Index'] = range(len(trends_df))
        
        slope, _, _, _, _ = stats.linregress(trends_df['Time_Index'], trends_df['Interest'])
        return slope
    except FileNotFoundError:
        print(f"Warning: File not found at {csv_file_path}. Returning slope of 0.")
        return 0
    except Exception as e:
        print(f"An error occurred with file {csv_file_path}: {e}")
        return 0

trends_file_mapping = {
    "Software Engineer": "../data/raw/trends/trends_software_engineer.csv",
    "Software Developer": "../data/raw/trends/trends_software_developer.csv",
    "Frontend Developer" : "../data/raw/trends/trends_frontend_developer.csv",
    "FullStack Developer" : "../data/raw/trends/trends_fullstack_developer.csv",
    "Backend Developer" : "../data/raw/trends/trends_backend_developer.csv",
    "Data Analyst": "../data/raw/trends/trends_data_analyst.csv",
    "AI/ML Engineer": "../data/raw/trends/trends_aiml_engineer.csv",
    "DevOps": "../data/raw/trends/trends_devops.csv",
    "CyberSecurity Analyst" : "../data/raw/trends/trends_cybersecurity_analyst.csv",
    "Business Analyst" : "../data/raw/trends/trends_business_analyst.csv",
    "App Developer" : "../data/raw/trends/trends_app_developer.csv",
    "Software Tester" : "../data/raw/trends/trends_software_tester.csv",
    "Technical Support" : "../data/raw/trends/trends_technical_support.csv", 
    "Network Engineer" : "../data/raw/trends/trends_network_engineer.csv" ,
    "Product Engineer" : "../data/raw/trends/trends_product_engineer.csv"
}

def process_raw_data(raw_df, trends_mapping):

    processed_df = raw_df.copy()
    processed_df['avg_salary_inr'] = processed_df['Salary_Range_INR (lakhs)'].apply(clean_salary)
    processed_df['skills_list'] = processed_df['Skills_Required'].apply(parse_skills)
    processed_df['standard_date'] = processed_df['Posting_Date'].apply(standardize_date)
    processed_df['fgm_score'] = processed_df['Standard_Title'].map(trends_mapping).apply(get_trend_slope)
    
    return processed_df