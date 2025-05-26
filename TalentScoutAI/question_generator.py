import os
import requests
import json
import time
from typing import Optional, Dict, Any

class QuestionGenerator:
    """
    Generates technical questions using Hugging Face Inference API.
    """
    
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Alternative models to try if primary fails
        self.alternative_models = [
            "microsoft/DialoGPT-large",
            "google/flan-t5-large",
            "facebook/blenderbot-400M-distill"
        ]
        
        # Cache for generated questions to avoid regenerating
        self.question_cache = {}
    
    def generate_question(self, technology: str, question_number: int) -> Optional[str]:
        """
        Generate a technical question for the specified technology.
        
        Args:
            technology: The technology/framework to generate questions for
            question_number: The number of the question (1-5 typically)
            
        Returns:
            Generated technical question or None if generation fails
        """
        
        # Check cache first
        cache_key = f"{technology.lower()}_{question_number}"
        if cache_key in self.question_cache:
            return self.question_cache[cache_key]
        
        if not self.api_key:
            print("Warning: HUGGINGFACE_API_KEY not found in environment variables")
            return None
        
        # Create context-aware prompt for question generation
        prompt = self._create_question_prompt(technology, question_number)
        
        # Try primary model first
        question = self._call_huggingface_api(prompt, self.api_url)
        
        # Try alternative models if primary fails
        if not question:
            for model in self.alternative_models:
                alt_url = f"https://api-inference.huggingface.co/models/{model}"
                question = self._call_huggingface_api(prompt, alt_url)
                if question:
                    break
        
        # Clean and validate the generated question
        if question:
            cleaned_question = self._clean_question(question)
            if cleaned_question:
                # Cache the question
                self.question_cache[cache_key] = cleaned_question
                return cleaned_question
        
        return None
    
    def _create_question_prompt(self, technology: str, question_number: int) -> str:
        """Create an effective prompt for question generation."""
        
        difficulty_levels = {
            1: "basic",
            2: "intermediate", 
            3: "advanced"
        }
        
        difficulty = difficulty_levels.get(question_number, "intermediate")
        
        prompt = f"""<s>[INST] You are a technical interviewer. Generate one {difficulty} level technical interview question about {technology}. The question should test practical knowledge and be answerable in 2-3 minutes. Only return the question, nothing else. [/INST]

Here's a {difficulty} technical question about {technology}:"""
        
        return prompt
    
    def _call_huggingface_api(self, prompt: str, api_url: str, max_retries: int = 3) -> Optional[str]:
        """
        Call Hugging Face Inference API with retry logic.
        
        Args:
            prompt: The input prompt for question generation
            api_url: The API endpoint URL
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated text or None if all attempts fail
        """
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 150,
                "min_length": 20,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Handle different response formats
                    if isinstance(result, list) and len(result) > 0:
                        if 'generated_text' in result[0]:
                            return result[0]['generated_text'].strip()
                        elif 'text' in result[0]:
                            return result[0]['text'].strip()
                    elif isinstance(result, dict):
                        if 'generated_text' in result:
                            return result['generated_text'].strip()
                        elif 'text' in result:
                            return result['text'].strip()
                
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    print(f"Model loading, waiting {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                    continue
                    
                else:
                    print(f"API call failed with status {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                continue
            except Exception as e:
                print(f"Unexpected error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                continue
        
        return None
    
    def _clean_question(self, raw_question: str) -> Optional[str]:
        """
        Clean and validate the generated question.
        
        Args:
            raw_question: Raw output from the API
            
        Returns:
            Cleaned question or None if validation fails
        """
        
        if not raw_question:
            return None
        
        # Remove common artifacts and clean up
        question = raw_question.strip()
        
        # Remove "Question:" prefix if present
        if question.lower().startswith("question:"):
            question = question[9:].strip()
        
        # Remove quotes if the entire question is quoted
        if question.startswith('"') and question.endswith('"'):
            question = question[1:-1].strip()
        if question.startswith("'") and question.endswith("'"):
            question = question[1:-1].strip()
        
        # Split by newlines and take the first substantial line
        lines = [line.strip() for line in question.split('\n') if line.strip()]
        if lines:
            question = lines[0]
        
        # Ensure question ends with a question mark
        if question and not question.endswith('?'):
            question += '?'
        
        # Validate question quality
        if self._validate_question(question):
            return question
        
        return None
    
    def _validate_question(self, question: str) -> bool:
        """
        Validate that the generated question meets quality criteria.
        
        Args:
            question: The question to validate
            
        Returns:
            True if question is valid, False otherwise
        """
        
        if not question:
            return False
        
        # Basic length check
        if len(question) < 10 or len(question) > 300:
            return False
        
        # Must end with question mark
        if not question.endswith('?'):
            return False
        
        # Should contain some technical keywords
        technical_indicators = [
            'what', 'how', 'why', 'explain', 'describe', 'implement',
            'difference', 'compare', 'advantage', 'disadvantage',
            'when', 'where', 'which', 'define', 'demonstrate'
        ]
        
        question_lower = question.lower()
        if not any(indicator in question_lower for indicator in technical_indicators):
            return False
        
        # Avoid obviously bad questions
        bad_patterns = [
            'i don\'t know',
            'sorry',
            'cannot',
            'unable',
            'error',
            'failed'
        ]
        
        if any(pattern in question_lower for pattern in bad_patterns):
            return False
        
        return True
    
    def get_cached_questions(self) -> Dict[str, str]:
        """Return all cached questions."""
        return self.question_cache.copy()
    
    def clear_cache(self) -> None:
        """Clear the question cache."""
        self.question_cache.clear()
