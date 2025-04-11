import streamlit as st
import requests
import uuid
import time
import json
from datetime import datetime

# Configuration
# Update with your API URL
API_URL = "https://3o4zk1nlhg.execute-api.us-east-1.amazonaws.com/prod"
HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": "iAA8smqAS0aOg3MftZvkU2q62xrq5MRC5dQia4Vm"
}

# Set page configuration
st.set_page_config(
    page_title="Peely Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Ensure text colors are dark on light backgrounds */
    .user-message {
        background-color: #e6f3ff;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        color: #111827 !important;
    }
    .bot-message {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        color: #111827 !important;
    }
    .sources {
        font-size: 0.8em;
        color: #555 !important;
        border-top: 1px solid #ddd;
        padding-top: 5px;
        margin-top: 5px;
    }
    .timestamp {
        font-size: 0.7em;
        color: #777 !important;
        text-align: right;
    }
    .stButton button {
        width: 100%;
    }
    .conversation-info {
        background-color: #f9f9f9;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 20px;
        color: #111827 !important;
    }

</style>
""", unsafe_allow_html=True)

# Function to create a new conversation


def create_conversation():
    try:
        response = requests.post(f"{API_URL}/conversations", headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("conversationId")
        else:
            st.error(f"Error creating conversation: {response.text}")
            # Fallback to using a generated UUID
            return str(uuid.uuid4())
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        # Fallback to using a generated UUID
        return str(uuid.uuid4())

# Function to send a message and get a response


def send_message(conversation_id, message):
    try:
        start_time = time.time()

        response = requests.post(
            f"{API_URL}/conversations/{conversation_id}/messages",
            json={"message": message},
            headers=HEADERS
        )

        end_time = time.time()
        response_time = end_time - start_time

        if response.status_code == 200:
            resp_data = response.json()
            resp_data["response_time"] = response_time
            return resp_data
        else:
            st.error(f"Error sending message: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

# Function to get all conversations


def get_conversations():
    try:
        response = requests.get(f"{API_URL}/conversations", headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("conversations", [])
        else:
            st.error(f"Error getting conversations: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

# Function to load a conversation


def load_conversation(conversation_id):
    try:
        response = requests.get(f"{API_URL}/conversations/{conversation_id}", headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("messages", [])
        else:
            st.error(f"Error loading conversation: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

# Function to format timestamp


def format_timestamp(timestamp):
    if not timestamp:
        return ""
    dt = datetime.fromtimestamp(timestamp / 1000)
    return dt.strftime("%H:%M:%S - %b %d, %Y")


# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = create_conversation()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversations" not in st.session_state:
    st.session_state.conversations = []

if "show_api_info" not in st.session_state:
    st.session_state.show_api_info = False

# App layout
st.title("🤖 Peely Chatbot")

# Sidebar
with st.sidebar:
    st.header("About Peely")
    st.write("""
    Peely is a cost-effective AI chatbot built with:
    - 🧠 AWS Bedrock (Claude from Anthropic)
    - 🔍 Pinecone Vector Database
    - ⚡ AWS Lambda Serverless Functions
    - 📦 DynamoDB for conversation history
    """)

    st.subheader("Options")

    if st.button("🆕 New Conversation"):
        st.session_state.conversation_id = create_conversation()
        st.session_state.messages = []
        st.rerun()

    # API info toggle
    if st.button("⚙️ Toggle API Info"):
        st.session_state.show_api_info = not st.session_state.show_api_info

    if st.session_state.show_api_info:
        st.code(f"API Endpoint: {API_URL}")
        st.code(f"Current Conversation ID: {st.session_state.conversation_id}")

    # Try to load conversations
    try:
        st.subheader("Load Conversation")
        if st.button("🔄 Refresh Conversations"):
            st.session_state.conversations = get_conversations()

        if st.session_state.conversations:
            selected_conversation = st.selectbox(
                "Select a conversation:",
                st.session_state.conversations
            )

            if st.button("Load Selected Conversation"):
                st.session_state.conversation_id = selected_conversation
                st.session_state.messages = load_conversation(
                    selected_conversation)
                st.rerun()
    except Exception:
        st.write("Cannot load conversation list.")

# Main chat interface
chat_container = st.container()

# Display conversation info
with chat_container:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Conversation with Peely")
    with col2:
        st.markdown(
            f"<div class='timestamp'>ID: {st.session_state.conversation_id[:8]}...</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong><br>
                {message['content']}
                <div class="timestamp">{format_timestamp(message.get('timestamp', None))}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bot-message">
                <strong>Peely:</strong><br>
                {message['content']}
            """, unsafe_allow_html=True)

            # Display sources if available
            if "sources" in message and message["sources"]:
                unique_sources = list(set(message["sources"]))
                sources_html = "<div class='sources'>Sources:<br>"
                for source in unique_sources:
                    sources_html += f"• {source}<br>"
                sources_html += "</div>"
                st.markdown(sources_html, unsafe_allow_html=True)

            # Display response time if available
            if "response_time" in message:
                st.markdown(f"""
                <div class="timestamp">
                    Response time: {message['response_time']:.2f}s<br>
                    {format_timestamp(message.get('timestamp', None))}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="timestamp">{format_timestamp(message.get('timestamp', None))}</div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

# Input for new messages
with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_area("Your message:", key="user_input", height=100)

    cols = st.columns([3, 1])
    with cols[0]:
        submit_button = st.form_submit_button("📤 Send Message")
    with cols[1]:
        clear_button = st.form_submit_button("🗑️ Clear Chat")

    if clear_button:
        st.session_state.messages = []
        st.rerun()

    if submit_button and user_input.strip():
        # Add user message to chat
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": int(time.time() * 1000)
        }
        st.session_state.messages.append(user_message)

        # Show a spinner while waiting for response
        with st.spinner("Peely is thinking..."):
            # Send message to API
            response = send_message(
                st.session_state.conversation_id, user_input)

            if response:
                # Add bot response to chat
                bot_message = {
                    "role": "assistant",
                    "content": response.get("message", "Sorry, I couldn't generate a response."),
                    "sources": response.get("sources", []),
                    "timestamp": response.get("timestamp", int(time.time() * 1000)),
                    "response_time": response.get("response_time", 0)
                }
                st.session_state.messages.append(bot_message)

        # Force a rerun to update the chat display
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 0.8em;">
        Powered by AWS Bedrock, Lambda, and Pinecone | 
        Built with Streamlit | 
        © 2025 Peely Chatbot
    </div>
    """,
    unsafe_allow_html=True
)
