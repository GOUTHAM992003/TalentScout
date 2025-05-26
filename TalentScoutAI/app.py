import streamlit as st
import requests
import re
import os
from chatbot import TalentScoutChatbot

# Initialize the chatbot
chatbot = TalentScoutChatbot()

# Configure Streamlit for Render
st.set_page_config(
    page_title="🤖 TalentScout Hiring Assistant",
    layout="centered"
)

# Set Hugging Face API key (from environment variable)
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
if not HF_API_KEY:
    st.error("Hugging Face API key not found. Please set HUGGINGFACE_API_KEY environment variable.")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.stage = "greet"

def generate_questions(tech_stack):
    """Generate questions using Hugging Face API"""
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    prompt = f"""Generate 5 technical interview questions about: {tech_stack}
    - Include 1 architecture, 2 implementation, 1 optimization, and 1 advanced question
    - Format as a numbered list"""
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        return None

# Main chat interface
st.title("🤖 TalentScout Hiring Assistant")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Handle user input
if prompt := st.chat_input("Your response..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get chatbot response
    response = chatbot.process_input(prompt)
    
    # Generate questions if at tech stack stage
    if chatbot.conversation_state == "tech_stack":
        tech_stack = prompt
        questions = generate_questions(tech_stack)
        if questions:
            response = f"🔍 Technical Questions:\n{questions}\n\n✅ Screening complete!"
    
    with st.chat_message("assistant"):
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Required for Render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8501))
    st.rerun()
