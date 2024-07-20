import boto3
import json
import logging
import os


generator_logger = logging.getLogger('__name__')


class Generator:
    def __init__(self, config, model=None, tokenizer=None):
        self.config = config
        self.region_name = config['model']['llm']['region_name']
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.model_id = config['model']['llm']['model_id']
        self.anthropic_version = config['model']['llm']['anthropic_version']
        self.max_tokens = config['model']['llm']['max_tokens']
                
    def generate(self, user_prompt, system_prompt=None):
        try:
            bedrock_runtime = boto3.client(service_name='bedrock-runtime',
                                        region_name=self.region_name,
                                        aws_access_key_id=self.aws_access_key_id,
                                        aws_secret_access_key=self.aws_secret_access_key)

            user_message =  {"role": "user", "content": user_prompt}
            messages = [user_message]

            body=json.dumps(
                {
                    "anthropic_version": self.anthropic_version,
                    "max_tokens": self.max_tokens,
                    "system": system_prompt,
                    "messages": messages,
                    "temperature": self.config['model']['llm']['temperature'],
                    "top_k": self.config['model']['llm']['top_k'],
                }
            )

            response = bedrock_runtime.invoke_model(body=body, modelId=self.model_id)
            response_body = json.loads(response.get('body').read())['content'][0]["text"]
            return response_body
        
        except Exception as e:
                generator_logger.error(e, exc_info=True)
