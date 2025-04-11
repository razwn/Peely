import os
from langchain_openai import OpenAIEmbeddings


def get_embedding_model():
    """Initialize and return OpenAI embedding model"""
    return OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=os.environ['OPENAI_API_KEY']
    )
