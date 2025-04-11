import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


def test_pinecone_basic():
    """Test basic Pinecone connection without LangChain integration"""
    try:
        # Get API keys from environment
        pinecone_api_key = os.environ.get('PINECONE_API_KEY')
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        index_name = os.environ.get('PINECONE_INDEX_NAME')

        if not all([pinecone_api_key, openai_api_key, index_name]):
            print("Error: Missing required environment variables.")
            print(
                "Make sure PINECONE_API_KEY, OPENAI_API_KEY, and PINECONE_INDEX_NAME are set.")
            return False

        # Initialize Pinecone
        print(f"Initializing Pinecone with API key: {pinecone_api_key[:5]}...")
        pc = Pinecone(api_key=pinecone_api_key)

        # List available indexes
        indexes = pc.list_indexes().names()
        print(f"Available indexes: {indexes}")

        # Check if our index exists
        if index_name not in indexes:
            print(f"Creating new index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=1536,  # OpenAI embeddings dimension
                metric="cosine"
            )

        # Get the index
        print(f"Connecting to index: {index_name}")
        index = pc.Index(index_name)

        # Create OpenAI client for embeddings
        openai_client = OpenAI(api_key=openai_api_key)

        # Generate an embedding
        test_text = "Hello, this is a test query for Pinecone."
        print(f"Generating embedding for text: '{test_text}'")
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=test_text
        )
        embedding = embedding_response.data[0].embedding

        # Upsert a test vector
        print("Upserting test vector to Pinecone")
        index.upsert(
            vectors=[
                {
                    "id": "test-vector-1",
                    "values": embedding,
                    "metadata": {"text": test_text}
                }
            ]
        )

        # Query to test retrieval
        print("Querying Pinecone")
        query_response = index.query(
            vector=embedding,
            top_k=1,
            include_metadata=True
        )

        # Print results
        print("Query results:")
        for match in query_response["matches"]:
            print(f"  ID: {match['id']}")
            print(f"  Score: {match['score']}")
            print(f"  Metadata: {match['metadata']}")

        print("Pinecone connection test completed successfully!")
        return True

    except Exception as e:
        print(f"Error testing Pinecone: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pinecone_basic()
    if success:
        print("All tests passed!")
    else:
        print("Tests failed.")
