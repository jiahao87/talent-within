from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os

from engines.llm_generator import Generator
from engines.extraction import ExtractionEngine
from utils.load_config import load_config
from utils.load_env_var import load_env_var


config = load_config()
load_env_var()
app = FastAPI(docs_url="/doc")

llm_generator = Generator(config)
extraction_engine = ExtractionEngine(config, llm_generator)


class Filepath(BaseModel):
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

    
if __name__ == '__main__':
    uvicorn.run(app, port=config['api']['port'], host=config['api']['url'], workers=config['api']['workers_num'])
