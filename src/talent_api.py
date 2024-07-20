from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
import uvicorn
import os

from engines.llm_generator import Generator
from engines.extraction import ExtractionEngine
from engines.scoring import ScoringEngine
from utils.load_config import load_config
from utils.load_env_var import load_env_var


config = load_config()
load_env_var()
app = FastAPI(docs_url="/doc")

llm_generator = Generator(config)
extraction_engine = ExtractionEngine(config, llm_generator)
scoring_engine = ScoringEngine(config, llm_generator)


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


@app.post("/extract-cv")
def extract_cv(filepath: Filepath):   
    cv_json = extraction_engine.extract_cv(filepath.filepath)
    return cv_json

@app.post("/extract-all-cv")
def extract_all_cv():   
    cv_json = extraction_engine.extract_cv_from_folder()
    return cv_json

@app.post("/talent-matching")
def talent_matching(jd: JDdetails):
    candidate_results = scoring_engine.score_all_candidates(jd.dict())
    return status.HTTP_200_OK
    
if __name__ == '__main__':
    uvicorn.run(app, port=config['api']['port'], host=config['api']['url'], workers=config['api']['workers_num'])
