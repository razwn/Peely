import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from utils.embedding_utils import get_embedding_model

load_dotenv()


def get_pinecone_index():
    """Initialize and return Pinecone vectorstore with OpenAI embeddings"""
    # Initialize Pinecone client
    pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])

    # Get index name from environment variables
    index_name = os.environ['PINECONE_INDEX_NAME']

    # Get embedding model
    embedding_model = get_embedding_model()

    # Check if index exists, if not create it
    existing_indexes = [idx for idx in pc.list_indexes().names()]
    if index_name not in existing_indexes:
        # Create index
        pc.create_index(
            name=index_name,
            dimension=1536,  # For OpenAI ada-002 embeddings
            metric="cosine"
        )

    # Get the index object
    pinecone_index = pc.Index(index_name)

    # Initialize the vector store
    vectorstore = PineconeVectorStore(
        index=pinecone_index,
        embedding=embedding_model,
        text_key="text"
    )

    return vectorstore
