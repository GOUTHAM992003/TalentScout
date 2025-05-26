# TalentScout Hiring Assistant 🎯

An intelligent AI-powered chatbot for initial candidate screening in recruitment processes. Built with Streamlit and powered by Hugging Face language models.

## 📋 Project Overview

TalentScout is a conversational hiring assistant that streamlines the initial candidate screening process. The chatbot collects essential candidate information and generates tailored technical questions based on their declared tech stack using advanced language models.

### Key Features

- **Interactive Streamlit Interface**: Clean, user-friendly web interface
- **Information Gathering**: Collects name, email, phone, experience, position, location, and tech stack
- **AI-Powered Technical Questions**: Generates 3-5 relevant technical questions per technology using Hugging Face API
- **Context-Aware Conversations**: Maintains conversation flow and handles follow-up interactions
- **GDPR Compliance**: Implements data privacy best practices and candidate data protection
- **Fallback Mechanisms**: Handles unexpected inputs gracefully
- **Progress Tracking**: Visual progress indicator for candidates

## 🚀 Installation Instructions

### Prerequisites

- Python 3.8 or higher
- Hugging Face API key (free account at https://huggingface.co/)

### Setup Steps

1. **Clone or download the project files**
   ```bash
   # If using git
   git clone <repository-url>
   cd talentscout-hiring-assistant
   
   # Or extract the provided zip file
   unzip TalentScoutEnhancer.zip
   cd TalentScoutEnhancer
   ```

2. **Install required dependencies**
   ```bash
   pip install streamlit requests
   ```

3. **Set up environment variables**
   
   **Option A: Environment Variable**
   ```bash
   export HUGGINGFACE_API_KEY="your_huggingface_api_key_here"
   ```
   
   **Option B: Create .env file** (if using python-dotenv)
   ```bash
   echo "HUGGINGFACE_API_KEY=your_huggingface_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   streamlit run app.py --server.port 5000
   ```

5. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`
   - The application will be ready for candidate interactions

## 💡 Usage Guide

### For Candidates

1. **Start Interview**: Click "Start Interview" to begin the screening process
2. **Provide Information**: Answer questions about your background step by step:
   - Full name
   - Email address
   - Phone number
   - Years of experience
   - Desired position(s)
   - Current location
   - Technical skills/tech stack

3. **Technical Assessment**: Answer AI-generated technical questions based on your declared skills
4. **Complete Interview**: Review the summary and receive next steps information

### For HR/Recruiters

- Candidate data is automatically saved in the `candidate_data/` directory
- Each candidate session generates a timestamped JSON file
- Data includes candidate information, tech stack, and questions asked
- Progress tracking available in the sidebar during active sessions

### Conversation Controls

- Type `exit`, `quit`, `bye`, or `goodbye` to end the conversation at any time
- The chatbot provides guidance if inputs are unclear
- Progress indicator shows completion percentage


## ❗ Known Issues
Hugging Face API errors:
- Free tier may have rate limits (wait 20 sec between requests)
- Fallback questions activate when API fails
