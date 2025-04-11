import requests
import json
import sys

# Replace with your actual API Gateway URL from the CDK output
API_URL = "https://1fkonqxkh4.execute-api.us-east-1.amazonaws.com/prod"


def test_api():
    print(f"Testing API URL: {API_URL}")

    # Create a new conversation
    print("\n1. Creating a new conversation...")
    try:
        response = requests.post(f"{API_URL}/conversations")
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        print(f"Response status: {response.status_code}")
        print(f"Response body: {json.dumps(response.json(), indent=2)}")

        conversation_id = response.json().get("conversationId")
        if not conversation_id:
            print("Failed to get conversation ID from response")
            return

        print(f"Conversation ID: {conversation_id}")

        # Send a test message
        print("\n2. Sending a test message...")
        message_response = requests.post(
            f"{API_URL}/conversations/{conversation_id}/messages",
            json={"message": "What can you tell me about Cademan Wood?"}
        )
        message_response.raise_for_status()

        print(f"Response status: {message_response.status_code}")
        print(
            f"Response body: {json.dumps(message_response.json(), indent=2)}")

        # Extract and print the message
        ai_message = message_response.json().get("message", "No response")
        print("\nPeely's response:")
        print("-" * 80)
        print(ai_message)
        print("-" * 80)

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Check if URL has been updated
    if "your-api-id" in API_URL:
        print("Error: You need to update the API_URL with your actual API Gateway URL")
        sys.exit(1)

    test_api()
