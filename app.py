import streamlit as st
import os
from dotenv import load_dotenv

# Force reload of environment variables
os.environ.clear()
load_dotenv(override=True)

# Write debug info to a file
with open("debug.log", "w") as f:
    f.write(f"CHATBOT_API_URL = {os.getenv('CHATBOT_API_URL')}\n")
    f.write(f"Current working directory = {os.getcwd()}\n")

from api_service import send_message, get_conversation_messages
import io
import json

st.set_page_config(page_title="Cal.com Scheduler Chatbot", page_icon="🤖", layout="centered")

# --- Welcome Message ---
st.title("Cal.com Scheduler Chatbot 🤖")
st.markdown("""
Welcome! This chatbot helps you manage your Cal.com meetings.\
Enter your email to start a new session. Your chat history will be saved for this session only.
""")

# --- User Email Input ---
if "user_email" not in st.session_state:
    st.session_state.user_email = st.text_input("Enter your email to start:")
    st.stop()
else:
    st.session_state.user_email = st.text_input("Enter your email to start:", value=st.session_state.user_email)
    if not st.session_state.user_email:
        st.stop()

# Display environment info for debugging
with st.expander("Debug Info"):
    st.write(f"API URL: {os.getenv('CHATBOT_API_URL')}")
    st.write(f"Working Directory: {os.getcwd()}")

# --- Conversation State ---
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "error" not in st.session_state:
    st.session_state.error = None

# --- Chat Controls ---
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🧹 Clear Conversation"):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.session_state.error = None
        st.experimental_rerun()
with col2:
    if st.session_state.messages:
        chat_text = io.StringIO()
        for msg in st.session_state.messages:
            role = "You" if msg.get("role") == "user" else "Bot"
            chat_text.write(f"{role}: {msg['content']}\n")
        st.download_button("⬇️ Export Chat History", chat_text.getvalue(), file_name="chat_history.txt")

# --- Chat History Display ---
st.markdown("---")
st.subheader("Chat History")
if st.session_state.conversation_id:
    with st.spinner("Loading conversation history..."):
        try:
            history = get_conversation_messages(st.session_state.conversation_id)
            if isinstance(history, list):
                st.session_state.messages = history
                st.session_state.error = None
            elif isinstance(history, dict) and "error" in history:
                st.session_state.error = history["error"]
        except Exception as e:
            st.session_state.error = str(e)

# Display error if any
if st.session_state.error:
    st.error(f"Error: {st.session_state.error}")
    
    # Add a Retry button
    if st.button("Retry Connection"):
        st.session_state.error = None
        st.experimental_rerun()

for msg in st.session_state.messages:
    if msg.get("role") == "user":
        st.markdown(f"<div style='text-align: right; color: #2563eb;'><b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: left; color: #059669;'><b>Bot:</b> {msg['content']}</div>", unsafe_allow_html=True)

st.markdown("---")

# --- Message Input ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message:", key="user_input")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    # Add user message to local state first for immediate feedback
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("Bot is thinking..."):
        try:
            response = send_message(user_input, st.session_state.user_email, st.session_state.conversation_id)
            
            if "error" in response:
                st.session_state.error = response["error"]
                st.error(f"Error: {response['error']}")
            else:
                st.session_state.error = None
                st.session_state.conversation_id = response.get("conversation_id", st.session_state.conversation_id)
                # Add bot message to local state
                st.session_state.messages.append({"role": "assistant", "content": response.get("response", "")})
        except Exception as e:
            st.session_state.error = str(e)
            st.error(f"Error: {str(e)}")
    
    st.experimental_rerun()

# --- Footer ---
st.markdown("<hr style='margin-top:2em;'>", unsafe_allow_html=True)
st.caption("Built with Streamlit • Cal.com Scheduler Agent • Session chat only (refresh to reset)") 