import streamlit as st
import requests
from datetime import datetime

# API configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Loan Eligibility Assistant",
    page_icon="💰",
    layout="wide"
)

st.title("🏦 Loan Eligibility Assistant")
st.markdown("Check your eligibility for various loan products using our AI-powered chatbot")

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = "greeting"
if 'greeted' not in st.session_state:
    st.session_state.greeted = False

# Add initial greeting only once
if not st.session_state.greeted and not st.session_state.conversation:
    st.session_state.conversation.append({
        "role": "assistant",
        "content": "Hi 👋 I can help you check your loan eligibility. Please choose: 1️⃣ Personal Loan 2️⃣ Credit Card Loan",
        "timestamp": datetime.now().isoformat()
    })
    st.session_state.greeted = True

# Function to send message to backend
def send_message(message, session_id=None):
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"message": message, "session_id": session_id},
            timeout=10  # Add timeout to prevent hanging
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: Status code {response.status_code}")
            return {"error": True, "message": "Sorry, I'm having trouble connecting to the service."}
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return {"error": True, "message": "Sorry, I can't connect to the server right now. Please make sure the backend is running."}
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return {"error": True, "message": "An unexpected error occurred."}

# Main chat interface
st.header("Chat with Loan Assistant")

# Display conversation
for msg in st.session_state.conversation:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Assistant:** {msg['content']}")

# If conversation is completed, show restart button
if st.session_state.current_step == "completed":
    if st.button("Start New Conversation"):
        st.session_state.conversation = []
        st.session_state.session_id = None
        st.session_state.current_step = "greeting"
        st.session_state.greeted = False
        st.rerun()

# Chat input
if st.session_state.current_step != "completed":
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to conversation
        st.session_state.conversation.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })

        # Send to backend
        with st.spinner("Processing..."):
            response = send_message(user_input, st.session_state.session_id)

        # Debug: Show raw response
        st.sidebar.text(f"Raw response: {str(response)[:100]}...")

        # Handle response
        if "error" in response and response["error"]:
            assistant_content = response["message"]
            st.error(assistant_content)
        else:
            # Get response content safely
            assistant_content = response.get("response", response.get("message", "Sorry, I didn't get a response."))
            
            # Add assistant response to conversation
            st.session_state.conversation.append({
                "role": "assistant",
                "content": assistant_content,
                "timestamp": datetime.now().isoformat()
            })

            # Update session ID and current step
            st.session_state.session_id = response.get("session_id", st.session_state.session_id)
            st.session_state.current_step = response.get("current_step", st.session_state.current_step)

        # Force rerun to update the UI
        st.rerun()

# Sidebar with debug information
with st.sidebar:
    st.header("Debug Information")
    st.text(f"Session ID: {st.session_state.session_id}")
    st.text(f"Current Step: {st.session_state.current_step}")
    st.text(f"Message Count: {len(st.session_state.conversation)}")
    
    if st.button("Debug: Show Session State"):
        st.write(st.session_state)
    
    if st.button("Test API Connection"):
        try:
            test_response = requests.get(f"{API_BASE_URL}/", timeout=5)
            if test_response.status_code == 200:
                st.success("✅ Backend is connected!")
            else:
                st.error(f"❌ Backend returned status: {test_response.status_code}")
        except Exception as e:
            st.error(f"❌ Cannot connect to backend: {str(e)}")

    st.header("About This Service")
    st.markdown("""
    This AI-powered assistant helps you:
    - Check eligibility for personal loans and credit cards
    - Guide you through the application process
    - Provide personalized recommendations

    **Data Privacy:** Your information is secure and encrypted.
    We never store sensitive financial data.
    """)

    st.header("Eligibility Criteria")
    st.markdown("""
    - **Age:** 21-58 years
    - **Income:** ₹25,000+ per month
    - **Credit Score:** 750+ preferred
    - **Employment:** 1+ years stable employment
    - **Debt Ratio:** Existing EMIs < 50% of income
    """)

    if st.button("Clear Conversation"):
        st.session_state.conversation = []
        st.session_state.session_id = None
        st.session_state.current_step = "greeting"
        st.session_state.greeted = False
        st.rerun()

# Footer
st.markdown("---")
st.caption("🔒 Your data is protected and processed securely. We use advanced AI for eligibility assessment.")