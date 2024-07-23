import fitz
import json
import pandas as pd
from pathlib import Path
import re

from engines.prompt_catalog import *


class Guardrails:
    def __init__(self, config, llm):
        self.config = config
        self.llm = llm
        if Path(config['data']['cv_data']).is_file():
            self.cv_data_df = pd.read_excel(config['data']['cv_data'])
        else:
            self.cv_data_df = None

    def check_cv_data(self):
        if self.cv_data_df is not None:
            guardrail_results_list = []
            cv_data_list = json.loads(self.cv_data_df.to_json(orient="records"))
            for cv_data in cv_data_list:
                document = self.read_document(cv_data['filepath'])
                guardrail_results = self.check_extracted_data(cv_data, document)
                guardrail_results["filepath"] = cv_data['filepath']
                guardrail_results_list.append(guardrail_results)
                print(guardrail_results)
            guardrail_results_df = pd.DataFrame(guardrail_results_list)
            guardrail_results_df.to_excel(self.config['data']['guardrails_data'], index=False)

    def check_extracted_data(self, data_json, doc):
        system_prompt = system_prompt_guardrail
        user_prompt = user_prompt_guardrail.format(data_json=data_json, doc=doc)
        guardrail_results_str = self.llm.generate(user_prompt, system_prompt)
        guardrail_results_str = self.extract_json(guardrail_results_str)
        guardrail_results_json = json.loads(guardrail_results_str)
        return guardrail_results_json

    @staticmethod
    def extract_json(text):
        json_pattern = r'\{(?:[^{}]|\{[^{}]*\})*\}'
        match = re.search(json_pattern, text)
        if match:
            return match.group(0)
        else:
            return "{}"
        
    def read_document(self, filepath):
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        return text