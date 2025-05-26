import re
import json
from typing import Dict, List, Optional, Any
from ai_question_generator import AIQuestionGenerator

class TalentScoutChatbot:
    """
    Main chatbot class for TalentScout hiring assistant.
    Handles conversation flow, information gathering, and technical questioning.
    """
    
    def __init__(self):
        self.question_generator = AIQuestionGenerator()
        self.conversation_state = "greeting"
        self.candidate_data = {}
        self.technical_questions = []
        self.current_tech_index = 0
        self.questions_per_tech = 3
        
        # Define conversation flow states
        self.states = [
            "greeting", "name", "email", "phone", "experience", 
            "position", "location", "tech_stack", "technical_questions", "completed"
        ]
        
        # Required fields for validation
        self.required_fields = {
            "name": r"^[a-zA-Z\s]{2,50}$",
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "phone": r"^[\+]?[\d\s\-\(\)\.]{8,20}$"
        }
    
    def start_conversation(self) -> str:
        """Initialize the conversation with a greeting."""
        self.conversation_state = "name"
        return "Hi! I'm here to help with your application. **What's your full name?**"
    
    def process_input(self, user_input: str) -> str:
        """Process user input based on current conversation state."""
        user_input = user_input.strip()
        
        if not user_input:
            return "I didn't receive any input. Could you please try again?"
        
        # Handle different conversation states
        if self.conversation_state == "name":
            return self._handle_name(user_input)
        elif self.conversation_state == "email":
            return self._handle_email(user_input)
        elif self.conversation_state == "phone":
            return self._handle_phone(user_input)
        elif self.conversation_state == "experience":
            return self._handle_experience(user_input)
        elif self.conversation_state == "position":
            return self._handle_position(user_input)
        elif self.conversation_state == "location":
            return self._handle_location(user_input)
        elif self.conversation_state == "tech_stack":
            return self._handle_tech_stack(user_input)
        elif self.conversation_state == "technical_questions":
            return self._handle_technical_questions(user_input)
        else:
            return self._handle_fallback(user_input)
    
    def _handle_name(self, user_input: str) -> str:
        """Handle name collection."""
        if re.match(self.required_fields["name"], user_input):
            self.candidate_data["name"] = user_input
            self.conversation_state = "email"
            return f"Nice to meet you, {user_input}! 👋\n\n**What's your email address?**"
        else:
            return (
                "Please provide a valid full name (2-50 characters, letters and spaces only). "
                "**What's your full name?**"
            )
    
    def _handle_email(self, user_input: str) -> str:
        """Handle email collection."""
        if re.match(self.required_fields["email"], user_input):
            self.candidate_data["email"] = user_input
            self.conversation_state = "phone"
            return "Great! **What's your phone number?**"
        else:
            return (
                "Please provide a valid email address (e.g., john.doe@example.com). "
                "**What's your email address?**"
            )
    
    def _handle_phone(self, user_input: str) -> str:
        """Handle phone number collection."""
        if re.match(self.required_fields["phone"], user_input):
            self.candidate_data["phone"] = user_input
            self.conversation_state = "experience"
            return "Perfect! **How many years of professional experience do you have?**"
        else:
            return (
                "Please provide a valid phone number (8-15 digits, may include +, spaces, dashes, or parentheses). "
                "**What's your phone number?**"
            )
    
    def _handle_experience(self, user_input: str) -> str:
        """Handle experience collection."""
        # Extract years from input
        years_match = re.search(r'\d+', user_input)
        if years_match:
            years = int(years_match.group())
            if 0 <= years <= 50:
                self.candidate_data["experience"] = f"{years} years"
                self.conversation_state = "position"
                return "Excellent! **What position(s) are you interested in or applying for?**"
        
        return (
            "Please provide a valid number of years of experience (0-50 years). "
            "You can say something like '3 years' or just '3'. "
            "**How many years of professional experience do you have?**"
        )
    
    def _handle_position(self, user_input: str) -> str:
        """Handle desired position collection."""
        if len(user_input) >= 2:
            self.candidate_data["position"] = user_input
            self.conversation_state = "location"
            return "Great choice! **What's your current location (city, country)?**"
        else:
            return (
                "Please provide the position you're interested in (at least 2 characters). "
                "**What position(s) are you interested in or applying for?**"
            )
    
    def _handle_location(self, user_input: str) -> str:
        """Handle location collection."""
        if len(user_input) >= 2:
            self.candidate_data["location"] = user_input
            self.conversation_state = "tech_stack"
            return (
                "Perfect! Now let's talk about your technical skills. 💻\n\n"
                "**Please list your tech stack** - including programming languages, frameworks, "
                "databases, tools, and any other technologies you're proficient in. "
                "You can separate them with commas.\n\n"
                "*Example: Python, JavaScript, React, Django, PostgreSQL, Docker*"
            )
        else:
            return (
                "Please provide your current location (at least 2 characters). "
                "**What's your current location (city, country)?**"
            )
    
    def _handle_tech_stack(self, user_input: str) -> str:
        """Handle tech stack collection and initiate technical questions."""
        # Parse tech stack from user input
        tech_stack = [tech.strip() for tech in user_input.split(',') if tech.strip()]
        
        if len(tech_stack) >= 1:
            self.candidate_data["tech_stack"] = tech_stack
            self.conversation_state = "technical_questions"
            self.current_tech_index = 0
            
            # Generate first set of technical questions
            return self._generate_next_technical_questions()
        else:
            return (
                "Please provide at least one technology from your tech stack. "
                "You can separate multiple technologies with commas. "
                "**Please list your tech stack:**"
            )
    
    def _handle_technical_questions(self, user_input: str) -> str:
        """Handle technical question responses and progression."""
        # Store the answer (in a real implementation, you might want to evaluate answers)
        current_tech = self.candidate_data["tech_stack"][self.current_tech_index]
        
        # Move to next question or next technology
        if len(self.technical_questions) % self.questions_per_tech == 0:
            # Move to next technology
            self.current_tech_index += 1
            
            if self.current_tech_index >= len(self.candidate_data["tech_stack"]):
                # All technologies covered
                self.conversation_state = "completed"
                return self._complete_technical_assessment()
            else:
                # Generate questions for next technology
                return self._generate_next_technical_questions()
        else:
            # Generate next question for current technology
            return self._generate_next_technical_questions()
    
    def _generate_next_technical_questions(self) -> str:
        """Generate technical questions for current technology."""
        current_tech = self.candidate_data["tech_stack"][self.current_tech_index]
        
        # Check if this is the first question for this technology
        questions_for_current_tech = len(self.technical_questions) % self.questions_per_tech
        
        if questions_for_current_tech == 0:
            # First question for this technology
            intro_message = f"\n🔧 **Technical Assessment: {current_tech}**\n\n"
            intro_message += f"I'll ask you {self.questions_per_tech} questions about {current_tech}. "
            intro_message += "Please answer to the best of your ability.\n\n"
        else:
            intro_message = ""
        
        # Generate a question using the AI question generator (no fallback)
        question = self.question_generator.generate_question(
            current_tech, 
            questions_for_current_tech + 1
        )
        
        if question:
            self.technical_questions.append(question)
            question_num = questions_for_current_tech + 1
            return f"{intro_message}**Question {question_num} ({current_tech}):** {question}"
        else:
            # Skip to next technology if AI generation fails
            self.current_tech_index += 1
            if self.current_tech_index >= len(self.candidate_data["tech_stack"]):
                self.conversation_state = "completed"
                return self._complete_technical_assessment()
            else:
                return self._generate_next_technical_questions()
    
    def _complete_technical_assessment(self) -> str:
        """Complete the technical assessment and provide summary."""
        self.conversation_state = "completed"
        
        summary = "\n🎉 **Technical Assessment Complete!**\n\n"
        summary += f"Thank you for answering the technical questions! I've assessed your knowledge across "
        summary += f"{len(self.candidate_data['tech_stack'])} technologies: "
        summary += f"{', '.join(self.candidate_data['tech_stack'])}.\n\n"
        
        summary += "**Next Steps:**\n"
        summary += "• Our technical team will review your responses\n"
        summary += "• You'll receive an email within 2-3 business days with feedback\n"
        summary += "• If you advance, we'll schedule a technical interview\n"
        summary += "• For any questions, contact us at hr@talentscout.com\n\n"
        
        summary += "Is there anything else you'd like to know about the position or our company? "
        summary += "Otherwise, you can type 'exit' to end our conversation."
        
        return summary
    
    def _get_fallback_questions(self, technology: str) -> List[str]:
        """Provide fallback questions if API generation fails."""
        fallback_db = {
            "python": [
                "What are the differences between lists and tuples in Python?",
                "Explain the concept of decorators in Python with an example.",
                "How does Python's garbage collection work?"
            ],
            "javascript": [
                "Explain the difference between var, let, and const in JavaScript.",
                "What is event bubbling and how can you prevent it?",
                "How do closures work in JavaScript?"
            ],
            "react": [
                "What is the difference between state and props in React?",
                "Explain the React component lifecycle methods.",
                "What are React hooks and why are they useful?"
            ],
            "java": [
                "What is the difference between abstract classes and interfaces in Java?",
                "Explain the concept of polymorphism in Java.",
                "How does garbage collection work in Java?"
            ],
            "sql": [
                "What is the difference between INNER JOIN and LEFT JOIN?",
                "Explain what database normalization is and why it's important.",
                "How would you optimize a slow-running SQL query?"
            ]
        }
        
        # Try to find questions for the exact technology or a close match
        tech_lower = technology.lower()
        for key in fallback_db:
            if key in tech_lower or tech_lower in key:
                return fallback_db[key]
        
        # Generic programming questions if no specific match
        return [
            f"What do you consider best practices when working with {technology}?",
            f"Can you describe a challenging project where you used {technology}?",
            f"How do you stay updated with the latest developments in {technology}?"
        ]
    
    def _handle_fallback(self, user_input: str) -> str:
        """Handle unexpected inputs or states."""
        if self.conversation_state == "completed":
            return (
                "Our initial screening is complete! If you have any questions about the position "
                "or TalentScout, I'm happy to help. Otherwise, you can type 'exit' to end our conversation."
            )
        else:
            return (
                "I'm not sure I understand. Could you please provide the information I requested? "
                "If you need help, you can type 'exit' to end our conversation."
            )
    
    def end_conversation(self) -> str:
        """End the conversation gracefully."""
        self.conversation_state = "ended"
        
        message = "\n👋 **Thank you for your time!**\n\n"
        
        if self.candidate_data:
            message += "I've recorded all the information you provided. "
            
        message += (
            "Our team will review your details and get back to you soon.\n\n"
            "**Next Steps:**\n"
            "• Check your email for confirmation and next steps\n"
            "• Our team will contact you within 2-3 business days\n"
            "• Keep an eye out for updates about your application status\n\n"
            "**Contact Information:**\n"
            "📧 hr@talentscout.com\n"
            "📱 +1 (555) 123-4567\n"
            "🌐 www.talentscout.com\n\n"
            "Good luck with your application! 🍀"
        )
        
        return message
    
    def get_progress(self) -> int:
        """Calculate conversation progress percentage."""
        if self.conversation_state in self.states:
            current_index = self.states.index(self.conversation_state)
            return int((current_index / len(self.states)) * 100)
        return 0
