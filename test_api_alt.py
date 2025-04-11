import requests
import json
import sys
import uuid

# Replace with your actual API Gateway URL from the CDK output
API_URL = "https://1fkonqxkh4.execute-api.us-east-1.amazonaws.com/prod"


def test_api_direct_message():
    """Test the API by directly accessing a specific conversation ID"""
    print(f"Testing API URL: {API_URL}")

    # Generate a random conversation ID instead of creating one
    conversation_id = str(uuid.uuid4())
    print(f"Using generated conversation ID: {conversation_id}")

    # Send a test message directly
    print("\nSending a test message...")
    try:
        message_response = requests.post(
            f"{API_URL}/conversations/{conversation_id}/messages",
            json={"message": "What can you tell me about Cademan Wood?"}
        )

        print(f"Response status: {message_response.status_code}")

        if message_response.status_code == 200:
            print(
                f"Response body: {json.dumps(message_response.json(), indent=2)}")

            # Extract and print the message
            ai_message = message_response.json().get("message", "No response")
            print("\nPeely's response:")
            print("-" * 80)
            print(ai_message)
            print("-" * 80)
        else:
            print(f"Error response: {message_response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Check if URL has been updated
    if "your-api-id" in API_URL:
        print("Error: You need to update the API_URL with your actual API Gateway URL")
        sys.exit(1)

    test_api_direct_message()
