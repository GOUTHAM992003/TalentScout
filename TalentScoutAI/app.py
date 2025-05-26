import streamlit as st
import json
import datetime
from chatbot import TalentScoutChatbot
from database_handler import DatabaseHandler

def main():
    """Main Streamlit application for TalentScout Hiring Assistant"""
    
    # Page configuration
    st.set_page_config(
        page_title="TalentScout Hiring Assistant",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = TalentScoutChatbot()
        st.session_state.data_handler = DatabaseHandler()
        st.session_state.conversation_started = False
        st.session_state.conversation_ended = False
        st.session_state.messages = []
    
    # Header
    st.title("🎯 TalentScout Hiring Assistant")
    st.markdown("---")
    
    # Auto-start conversation with minimal greeting
    if not st.session_state.conversation_started:
        st.session_state.conversation_started = True
        initial_message = st.session_state.chatbot.start_conversation()
        st.session_state.messages.append({"role": "assistant", "content": initial_message})
        st.rerun()
    
    # Main chat interface
    if st.session_state.conversation_started and not st.session_state.conversation_ended:
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "assistant":
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(message["content"])
                else:
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message["content"])
        
        # Chat input
        user_input = st.chat_input("Type your response here...")
        
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Check for conversation ending keywords
            ending_keywords = ['exit', 'quit', 'bye', 'goodbye', 'end', 'stop']
            if any(keyword in user_input.lower() for keyword in ending_keywords):
                farewell_message = st.session_state.chatbot.end_conversation()
                st.session_state.messages.append({"role": "assistant", "content": farewell_message})
                st.session_state.conversation_ended = True
                
                # Save candidate data with technical questions
                if st.session_state.chatbot.candidate_data:
                    candidate_data = st.session_state.chatbot.candidate_data.copy()
                    candidate_data['technical_questions'] = st.session_state.chatbot.technical_questions
                    st.session_state.data_handler.save_candidate_data(candidate_data)
                
                st.rerun()
            else:
                # Process user input and get response
                response = st.session_state.chatbot.process_input(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    # Conversation ended state
    if st.session_state.conversation_ended:
        st.success("Thank you for completing the initial screening!")
        
        if st.session_state.chatbot.candidate_data:
            st.markdown("### Interview Summary")
            
            # Display collected information
            with st.expander("📋 Collected Information", expanded=True):
                data = st.session_state.chatbot.candidate_data
                col1, col2 = st.columns(2)
                
                with col1:
                    if data.get('name'):
                        st.write(f"**Name:** {data['name']}")
                    if data.get('email'):
                        st.write(f"**Email:** {data['email']}")
                    if data.get('phone'):
                        st.write(f"**Phone:** {data['phone']}")
                    if data.get('location'):
                        st.write(f"**Location:** {data['location']}")
                
                with col2:
                    if data.get('experience'):
                        st.write(f"**Experience:** {data['experience']}")
                    if data.get('position'):
                        st.write(f"**Desired Position:** {data['position']}")
                    if data.get('tech_stack'):
                        st.write(f"**Tech Stack:** {', '.join(data['tech_stack'])}")
            
            # Display technical questions asked
            if st.session_state.chatbot.technical_questions:
                with st.expander("🔧 Technical Questions Asked", expanded=False):
                    for i, question in enumerate(st.session_state.chatbot.technical_questions, 1):
                        st.write(f"{i}. {question}")
        
        # Reset option
        if st.button("Start New Interview", type="primary"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("### 📞 Contact Information")
        st.markdown("""
        **TalentScout Agency**  
        📧 hr@talentscout.com  
        📱 +1 (555) 123-4567  
        🌐 www.talentscout.com
        """)
        
        st.markdown("### 🔒 Privacy Notice")
        st.markdown("""
        Your information is handled in compliance with GDPR and data privacy standards. 
        All data collected during this screening will be used solely for recruitment purposes.
        """)
        
        if st.session_state.conversation_started:
            st.markdown("### 📊 Progress")
            progress = st.session_state.chatbot.get_progress()
            st.progress(progress / 100)
            st.write(f"{progress}% Complete")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    app.run()

