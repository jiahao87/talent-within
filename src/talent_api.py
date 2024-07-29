from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
from typing import List
import uvicorn
import json
import os

from engines.llm_generator import Generator
from engines.embedding import Embedding
from engines.extraction import ExtractionEngine
from engines.scoring import ScoringEngine
from engines.guardrails import Guardrails
from utils.load_config import load_config
from utils.load_env_var import load_env_var


config = load_config()
load_env_var()
app = FastAPI(docs_url="/doc")

llm_generator = Generator(config)
embedding_model = Embedding(config)
extraction_engine = ExtractionEngine(config, llm_generator, embedding_model)
scoring_engine = ScoringEngine(config, llm_generator, embedding_model)
guardrails = Guardrails(config, llm_generator)


class Filepath(BaseModel):
    filepath: str


class JDdetails(BaseModel):
    job_id: str
    job_title: str
    corporate_title: str
    country: str
    hiring_manager: str
    job_description: str
    ksa: List[str]
    ksa_reviewed: List[str]
    education: str
    years_of_experience: str
    technical_skill: List[str]
    non_technical_skill: List[str]
    domain_knowledge: List[str]
    language: List[str]
    filepath: str

    
@app.get("/")
async def root():
    return {f"""Welcome to Talent Within"""}


@app.post("/extract-jd")
def extract_jd(filepath: Filepath):   
    jd_json = extraction_engine.extract_jd(filepath.filepath)
    return jd_json

@app.post("/submit-jd")
def submit_jd(jd_details: JDdetails):

    output_path=config['data']['jobs_data']

    if os.path.exists(output_path):
        original_df = pd.read_excel(output_path, dtype={'job_id': str})
        existing_job_ids = list(original_df['job_id'].unique())
        results_job_id = str(jd_details.job_id)
        if results_job_id in existing_job_ids:
            original_df = original_df.loc[original_df['job_id']!=results_job_id].reset_index(drop=True)
        new_df = pd.concat([original_df, pd.DataFrame([jd_details.dict()])])

        new_df.to_excel(output_path, sheet_name="jd_details", index=False)
        
    else:
        pd.DataFrame([jd_details.dict()]).to_excel(output_path, sheet_name="jd_details", index=False)

@app.get("/list-jd")
def get_jd_list():
    jd_df = pd.read_excel(config["data"]["jobs_data"], usecols=["job_id", "job_title", "hiring_manager"])
    return json.loads(jd_df.to_json(orient="records"))

@app.post("/extract-cv")
def extract_cv(filepath: Filepath):   
    cv_json = extraction_engine.extract_cv(filepath.filepath)
    return cv_json

@app.post("/extract-all-cv")
def extract_all_cv():   
    cv_json = extraction_engine.extract_cv_from_folder()
    return cv_json

@app.post("/talent-matching")
def talent_matching(jd: JDdetails, background_tasks: BackgroundTasks):
    background_tasks.add_task(scoring_engine.score_all_candidates, jd.dict())
    # candidate_results = scoring_engine.score_all_candidates(jd.dict())
    return status.HTTP_200_OK

@app.get("/talent-results")
def get_talent_results(id: str):
    talent_results_df = pd.read_excel(config["data"]["results_data"], dtype={'job_id': str, 'Serial Number': str})
    talent_results_df = talent_results_df.loc[talent_results_df['job_id']==id]
    return json.loads(talent_results_df.to_json(orient="records"))

@app.get("/candidate-info")
def get_cv_file(id: str):
    cv_df = pd.read_excel(config["data"]["cv_data"], dtype={"employee_id": str})
    file_path = cv_df.loc[cv_df['employee_id']==id]['filepath'].values[0]
    return FileResponse(path=file_path, filename=file_path, media_type='application/pdf')

@app.post("/guardrails_check")
def guardrails_check():
    guardrails.check_cv_data()
    return status.HTTP_200_OK

    
if __name__ == '__main__':
    uvicorn.run(app, port=config['api']['port'], host=config['api']['url'], workers=config['api']['workers_num'])
