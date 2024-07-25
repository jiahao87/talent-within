import pandas as pd
from datetime import datetime
import json
import re
import os
from openpyxl import load_workbook
import numpy as np
from numpy.linalg import norm
import ast
import warnings
warnings.filterwarnings("ignore")

from engines.prompt_catalog import *


corporate_title_mapping = {"analyst": 1, "associate": 2, "vice president": 3, "executive director": 4, "managing director": 5}


class ScoringEngine:
    def __init__(self, config, llm, embedding_model):
        self.config = config
        self.llm = llm
        self.embedding_model = embedding_model
        self.cv_data_df = pd.read_excel(config['data']['cv_data'])
        self.employees_df = pd.read_excel(config['data']['employees_master_data'])
        self.employees_df = self.employees_df.loc[self.employees_df['Open to internal transfer']=="Yes"]
        self.process_manager_ratings()
        self.process_languages()

    def score_all_candidates(self, jd_details):
        candidates_df = self.preliminary_filtering(jd_details, self.config['model']['embedding']['top_n'])
        candidates_results = []
        candidates_list = candidates_df['Serial Number'].to_list()
        for candidate in candidates_list:
            try:
                candidate_data = json.loads(candidates_df.loc[candidates_df['Serial Number']==candidate].to_json(orient="records"))[0]
                score, ksa_list = self.score_candidate(jd_details, candidate_data)
                candidate_data['score'] = score
                candidate_data['ksa'] = ksa_list
                candidate_data.pop('job_history', None)
                candidates_results.append(candidate_data)
            except:
                continue
        candidate_results_df = pd.DataFrame(candidates_results)
        candidate_results_df['job_id'] = str(jd_details["job_id"])
        candidate_results_df.sort_values(by="score", ascending=False, inplace=True)
        self.save_extracted_data(candidate_results_df)
        return candidates_results    

    def preliminary_filtering(self, jd_details, top_n=20):
        candidates_prelim_df = self.employees_df.loc[(self.employees_df['Mobility']>=0.5) | (self.employees_df['Country']==jd_details["country"])]
        candidates_prelim_df['corporate_title_value'] = candidates_prelim_df['Global Corporate Title'].str.lower().map(corporate_title_mapping)
        jd_details['corporate_title_value'] = corporate_title_mapping[jd_details["corporate_title"].lower()]
        candidates_prelim_df['corporate_title_diff'] = candidates_prelim_df['corporate_title_value'] - jd_details['corporate_title_value']
        candidates_prelim_df = candidates_prelim_df.loc[(candidates_prelim_df['corporate_title_diff']==0) | (candidates_prelim_df['corporate_title_diff']==-1)]
        candidates_prelim_df = candidates_prelim_df.merge(self.cv_data_df, left_on="Serial Number", right_on="employee_id", how="left")
        candidates_prelim_df = candidates_prelim_df.loc[candidates_prelim_df['years_of_experience']>=int(jd_details["years_of_experience"])]

        jd_embedding = self.embed_jd(jd_details)
        candidates_prelim_df['similarity_score'] = candidates_prelim_df['embedding'].apply(lambda x: self.calculate_similarity_score(ast.literal_eval(x), jd_embedding))
        candidates_prelim_df.sort_values(by="similarity_score", ascending=False, inplace=True)
        candidates_prelim_df = candidates_prelim_df[["Serial Number", "First Name", "Last Name", "Division Org", "Product 1  Org", "Country", 
                                                     "Global Corporate Title", "Job Code Description", "education", "job_history", "technical_skill", 
                                                     "certification", "language_proficiency", "language", "manager_ratings", "last_hire_date", "filepath"]]
        
        return candidates_prelim_df[:top_n]
    
    def score_candidate(self, jd_details, candidate_data):
        jd = "Job Title: " + jd_details['job_title'] + "\n" + jd_details['job_description']
        relevant_experience = self.calculate_relevant_experience(jd, candidate_data['job_history'], candidate_data['last_hire_date'])
        candidate_data['relevant_years_of_experience'] = str(relevant_experience) + " year(s) of relevant experience"
        if 'years_of_experience' in candidate_data: 
            del candidate_data['years_of_experience']
        system_prompt = system_prompt_match_ksa
        ksa_reviewed = [ksa for ksa in jd_details["ksa_reviewed"] if ksa.lower()!="english"]
        user_prompt = user_prompt_relevant_experience.format(jd_data=ksa_reviewed, resume=candidate_data)
        match_results_str = self.llm.generate(user_prompt, system_prompt)
        match_results_str = self.extract_json(match_results_str)
        print(match_results_str)
        match_results_json = json.loads(match_results_str)
        num_matches = 0
        total_requirements = 0
        match_ksa = []
        for k, v in match_results_json.items():
            if v is not None:
                num_matches += 1
                if isinstance(v, (list, tuple)):
                    match_ksa.extend(v)
                else:
                    match_ksa.append(v)
            total_requirements += 1
        score = min(num_matches / total_requirements, 1)
        return score, list(set(match_ksa))

    def calculate_relevant_experience(self, jd, job_history, last_hire_date):
        now = datetime.now().strftime("%d %b %Y")
        system_prompt = system_prompt_relevant_experience.format(last_hire_date=last_hire_date, now=now)
        user_prompt = user_prompt_relevant_experience.format(jd_data=jd, resume=job_history)
        experience_str = self.llm.generate(user_prompt, system_prompt)
        pattern = r'\{[^{}]*"years_of_experience"[^{}]*\}'
        match = re.findall(pattern, experience_str)
        if match:
            years_of_experience_str = match[-1]
            try:
                years_of_experience_json = json.loads(years_of_experience_str)
                years_of_experience = years_of_experience_json['years_of_experience']
            except:
                years_of_experience = 0
        else:
            years_of_experience = 0
        return years_of_experience
    
    @staticmethod
    def extract_json(text):
        json_pattern = r'\{(?:[^{}]|\{[^{}]*\})*\}'
        match = re.search(json_pattern, text)
        if match:
            return match.group(0)
        else:
            return "{}"
    
    def process_manager_ratings(self):
        manager_rating_columns = [col for col in self.employees_df.columns.values.tolist() if "Manager Rating -"in col]

        for rating_col in manager_rating_columns:
            attribute_name = rating_col.replace("Manager Rating -", "").strip()
            ratings_mapping = {1: "", 2: "", 3: f"Good {attribute_name}", 4: f"Good {attribute_name}", 5: f"Good {attribute_name}"}
            self.employees_df[rating_col] = self.employees_df[rating_col].map(ratings_mapping)

        self.employees_df['manager_ratings'] = self.employees_df[manager_rating_columns].apply(lambda x: ', '.join(x.dropna().astype(str).values), axis=1)

    def process_languages(self):
        language_columns = [col for col in self.employees_df.columns.values.tolist() if "Language Literacy -"in col]
        self.employees_df['language_proficiency'] = self.employees_df[language_columns].apply(lambda x: ', '.join(x.dropna().astype(str).str.replace("-", "").values), axis=1)

    def save_extracted_data(self, df, output_path=None, sheetname="talent_results"):
        if output_path is None:
            output_path=self.config['data']['results_data']

        if os.path.exists(output_path):
            original_df = pd.read_excel(output_path, dtype={'job_id': str})
            existing_job_ids = list(original_df['job_id'].unique())
            results_job_id = list(df['job_id'].unique())[0]
            if results_job_id in existing_job_ids:
                original_df = original_df.loc[original_df['job_id']!=results_job_id].reset_index(drop=True)
            new_df = pd.concat([original_df, df])

            new_df.to_excel(output_path, sheet_name=sheetname, index=False)
            
        else:
            df.to_excel(output_path, sheet_name=sheetname, index=False)

    def embed_jd(self, jd):
        system_prompt = system_prompt_hypothetical_cv
        user_prompt = user_prompt_hypothetical_cv.format(job_description=str(jd))
        hypothetical_cv = self.llm.generate(user_prompt, system_prompt)
        jd_embedding = self.embedding_model.embed(hypothetical_cv)
        return jd_embedding

    def calculate_similarity_score(self, cv_embedding, jd_embedding):
        cosine = np.dot(jd_embedding,cv_embedding)/(norm(jd_embedding)*norm(cv_embedding))
        return cosine