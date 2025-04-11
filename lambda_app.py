import json
import os
import time
import boto3
import uuid
from dotenv import load_dotenv
from utils.pinecone_utils import get_pinecone_index
from utils.bedrock_utils import get_bedrock_llm
from utils.dynamodb_utils import save_conversation, get_conversation_history
from utils.embedding_utils import get_embedding_model
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError, InternalServerError
)

logger = Logger()
load_dotenv()

# Initialize API Gateway resolver
app = APIGatewayRestResolver()

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
conversation_table = dynamodb.Table(os.environ['CONVERSATION_TABLE_NAME'])

# Initialize helper components
try:
    logger.info("Initializing Pinecone index...")
    pinecone_index = get_pinecone_index()
    logger.info("Pinecone index initialized successfully")

    logger.info("Initializing embedding model...")
    embedding_model = get_embedding_model()
    logger.info("Embedding model initialized successfully")

    logger.info("Initializing Bedrock LLM...")
    llm = get_bedrock_llm(model_name=os.environ.get('CHOSEN_MODEL'))
    logger.info("Bedrock LLM model initialized successfully")

    # Create vector store
    logger.info("Creating vector store retriever...")
    vector_store = pinecone_index.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
    logger.info("Vector store retriever created successfully")
except Exception as e:
    logger.exception(f"Error initializing components: {str(e)}")
    raise

# Define standalone question prompt template (similar to article example)
standalone_question_prompt = PromptTemplate(
    template="""Given a chat history below and my latest question at the end
which might reference context in the chat history, formulate a standalone question
which can be understood without the chat history. Do NOT answer the question,
just reformulate it if needed and otherwise return it as is.

Chat history:
 {chat_history}

Based on the above conversation my latest question is this:
 {question}
""",
    input_variables=["chat_history", "question"]
)

# Create the conversational chain
conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store,
    condense_question_prompt=standalone_question_prompt,
    return_source_documents=True,
    verbose=True
)


@app.post("/conversations/<conversation_id>/messages")
def add_message(conversation_id):
    """Add a message to a conversation and get AI response"""
    try:
        # Parse request body
        body = app.current_event.body
        if isinstance(body, str):
            body = json.loads(body)

        user_message = body.get("message", "")

        if not user_message:
            raise BadRequestError("Message cannot be empty")

        # Get conversation history
        chat_history = get_conversation_history(
            conversation_table, conversation_id)

        # Save user message
        message_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)
        save_conversation(
            conversation_table,
            conversation_id,
            message_id,
            "user",
            user_message,
            timestamp
        )

        # Format chat history for LLM
        formatted_history = []
        for i in range(0, len(chat_history), 2):
            if i < len(chat_history):
                human_message = HumanMessage(content=chat_history[i])
                formatted_history.append(human_message)
                if i + 1 < len(chat_history):
                    ai_message = AIMessage(content=chat_history[i + 1])
                    formatted_history.append(ai_message)

        # Get response from LLM
        response = conversation_chain({
            "question": user_message,
            "chat_history": formatted_history
        })

        ai_message = response["answer"]
        source_docs = response.get("source_documents", [])

        # Extract source URLs (metadata)
        sources = []
        for doc in source_docs:
            if hasattr(doc, "metadata") and "source" in doc.metadata:
                sources.append(doc.metadata["source"])

        # Save AI response
        ai_message_id = str(uuid.uuid4())
        ai_timestamp = int(time.time() * 1000)
        save_conversation(
            conversation_table,
            conversation_id,
            ai_message_id,
            "ai",
            ai_message,
            ai_timestamp,
            sources
        )

        return {
            "messageId": ai_message_id,
            "conversationId": conversation_id,
            "message": ai_message,
            "sources": sources,
            "timestamp": ai_timestamp
        }

    except Exception as e:
        logger.exception("Error processing message")
        raise InternalServerError(f"Error processing message: {str(e)}")


@app.get("/conversations/<conversation_id>/messages")
def get_messages(conversation_id):
    """Get messages from a conversation"""
    try:
        chat_history = get_conversation_history(
            conversation_table, conversation_id)

        # Format as messages
        messages = []
        for i in range(len(chat_history)):
            entry = chat_history[i]
            messages.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": entry
            })

        return {
            "conversationId": conversation_id,
            "messages": messages
        }

    except Exception as e:
        logger.exception("Error retrieving messages")
        raise InternalServerError(f"Error retrieving messages: {str(e)}")


@app.get("/conversations")
def list_conversations():
    """List all conversations"""
    try:
        # In a real implementation, you'd want to filter by user ID
        # This is a simplified implementation
        response = conversation_table.scan(
            ProjectionExpression="conversation_id",
            Select="SPECIFIC_ATTRIBUTES"
        )

        # Extract unique conversation IDs
        conversation_ids = set()
        for item in response.get('Items', []):
            conversation_ids.add(item['conversation_id'])

        return {
            "conversations": list(conversation_ids)
        }

    except Exception as e:
        logger.exception("Error listing conversations")
        raise InternalServerError(f"Error listing conversations: {str(e)}")


@app.post("/conversations")
def create_conversation():
    """Create a new conversation"""
    try:
        conversation_id = str(uuid.uuid4())

        return {
            "conversationId": conversation_id
        }

    except Exception as e:
        logger.exception("Error creating conversation")
        raise InternalServerError(f"Error creating conversation: {str(e)}")


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> dict:
    """Lambda handler function"""
    return app.resolve(event, context)
