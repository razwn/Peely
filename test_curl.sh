#!/bin/bash

# Replace with your actual API Gateway URL from the CDK output
API_URL="https://1fkonqxkh4.execute-api.us-east-1.amazonaws.com/prod"

echo "Testing API URL: $API_URL"

# Create a new conversation
echo "Creating a new conversation..."
CONVERSATION_RESPONSE=$(curl -v -X POST "$API_URL/conversations")
echo "Raw response: $CONVERSATION_RESPONSE"

# Try to extract conversation ID
CONVERSATION_ID=$(echo $CONVERSATION_RESPONSE | grep -o '"conversationId":"[^"]*"' | cut -d'"' -f4)

if [ -z "$CONVERSATION_ID" ]; then
  echo "Failed to get conversation ID. Check if the API URL is correct."
  exit 1
fi

echo "Conversation ID: $CONVERSATION_ID"
echo

# Send a test message
echo "Sending test message..."
MESSAGE_RESPONSE=$(curl -v -X POST "$API_URL/conversations/$CONVERSATION_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"message":"What can you tell me about Cademan Wood?"}')

echo "Response from message API:"
echo "$MESSAGE_RESPONSE" | python -m json.tool

echo
echo "Test complete!"