import boto3
import json
import logging
import os


embedding_logger = logging.getLogger('__name__')


class Embedding:
    def __init__(self, config):
        self.config = config
        self.region_name = config['model']['embedding']['region_name']
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.model_id = config['model']['embedding']['model_id']
                
    def embed(self, text):
        try:
            bedrock_runtime = boto3.client(service_name='bedrock-runtime',
                                        region_name=self.region_name,
                                        aws_access_key_id=self.aws_access_key_id,
                                        aws_secret_access_key=self.aws_secret_access_key)
            
            body = json.dumps({
                "inputText": text,
            })

            # Invoke model 
            response = bedrock_runtime.invoke_model(
                body=body, 
                modelId=self.model_id, 
                accept='application/json' , 
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')
            return embedding
        
        except Exception as e:
                embedding_logger.error(e, exc_info=True)
