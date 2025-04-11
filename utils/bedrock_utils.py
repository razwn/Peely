import os
from langchain_aws import ChatBedrock
import boto3


def get_bedrock_llm(model_name: str = "claude") -> ChatBedrock:
    bedrock_region = os.environ.get('AWS_BEDROCK_REGION')

    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name=bedrock_region
    )
    if model_name == "claude":
        claude_llm = ChatBedrock(
            model_id=os.environ.get('BEDROCK_INFERENCE_PROFILE_ARN'),
            client=bedrock_client,
            model_kwargs={
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "top_k": 250,
                "temperature": 1,
                "top_p": 0.999,
            },
            provider="anthropic"
        )
        return claude_llm

    elif model_name == "mistral":
        mistral_llm = ChatBedrock(
            model_id=os.environ.get('BEDROCK_MISTRAL_MODEL_ID'),
            client=bedrock_client,
            model_kwargs={
                "max_tokens": 200,
                "top_k": 50,
                "temperature": 0.5,
                "top_p": 0.9,
            },
        )

        return mistral_llm
