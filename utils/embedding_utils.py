import os
import boto3
from langchain_aws import BedrockEmbeddings


embedding_model_id = os.environ.get('BEDROCK_EMBEDDING_MODEL_ID', 'amazon.titan-embed-text-v2:0')
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.environ.get("AWS_CHOSEN_REGION", "us-east-1"),
)


def get_embedding_model():
    """Initialize and return Bedrock embedding model"""
    return BedrockEmbeddings(
        model_id=embedding_model_id,
        client=bedrock_client
    )
