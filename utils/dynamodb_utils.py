from typing import List, Optional
import boto3
from boto3.dynamodb.conditions import Key


def save_conversation(
    table,
    conversation_id: str,
    message_id: str,
    role: str,
    content: str,
    timestamp: int,
    sources: Optional[List[str]] = None
):
    """Save a message to the conversation history in DynamoDB"""
    item = {
        'conversation_id': conversation_id,
        'message_id': message_id,
        'timestamp': timestamp,
        'role': role,
        'content': content
    }

    # Add sources if provided
    if sources:
        item['sources'] = sources

    # Put item in DynamoDB
    table.put_item(Item=item)


def get_conversation_history(table, conversation_id: str) -> List[str]:
    """Get conversation history from DynamoDB"""
    # Query items by conversation_id, sorted by timestamp
    response = table.query(
        KeyConditionExpression=Key('conversation_id').eq(conversation_id),
        ScanIndexForward=True  # Sort by timestamp ascending
    )

    # Extract messages in chronological order
    messages = []
    for item in response.get('Items', []):
        messages.append(item['content'])

    return messages
