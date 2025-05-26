import requests
import json
import time
from typing import Optional, Dict, Any

class AIQuestionGenerator:
    """
    Generates technical questions using free AI APIs.
    """
    
    def __init__(self):
        # Using free alternatives that don't require premium subscriptions
        self.api_urls = [
            "https://api.together.xyz/inference",
            "https://api.deepinfra.com/v1/inference"
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
        
        # Create a well-crafted prompt
        prompt = self._create_question_prompt(technology, question_number)
        
        # Try to generate using available methods
        question = self._generate_with_simple_ai(prompt, technology, question_number)
        
        if question:
            # Cache the question
            self.question_cache[cache_key] = question
            return question
        
        return None
    
    def _create_question_prompt(self, technology: str, question_number: int) -> str:
        """Create an effective prompt for question generation."""
        
        difficulty_levels = {
            1: "basic",
            2: "intermediate", 
            3: "advanced"
        }
        
        difficulty = difficulty_levels.get(question_number, "intermediate")
        
        return f"Generate a {difficulty} technical interview question about {technology} for a software developer position."
    
    def _generate_with_simple_ai(self, prompt: str, technology: str, question_number: int) -> Optional[str]:
        """
        Generate questions using a simple rule-based approach with technology-specific templates.
        This ensures we always get relevant technical questions without API dependencies.
        """
        
        tech_lower = technology.lower()
        difficulty_levels = {1: "basic", 2: "intermediate", 3: "advanced"}
        difficulty = difficulty_levels.get(question_number, "intermediate")
        
        # Comprehensive technology-specific question templates
        tech_questions = {
            # Programming Languages
            "python": {
                "basic": [
                    "What are the key differences between lists and tuples in Python?",
                    "Explain how Python's garbage collection works.",
                    "What is the difference between '==' and 'is' operators in Python?"
                ],
                "intermediate": [
                    "How do decorators work in Python? Provide an example.",
                    "Explain the concept of generators and their advantages over regular functions.",
                    "What are context managers in Python and how do you implement them?"
                ],
                "advanced": [
                    "How would you implement a metaclass in Python and when would you use it?",
                    "Explain the Global Interpreter Lock (GIL) and its impact on multithreading.",
                    "How would you optimize Python code for better performance?"
                ]
            },
            "javascript": {
                "basic": [
                    "What is the difference between var, let, and const in JavaScript?",
                    "Explain how hoisting works in JavaScript.",
                    "What are the different data types in JavaScript?"
                ],
                "intermediate": [
                    "How do closures work in JavaScript? Provide an example.",
                    "Explain event bubbling and event capturing.",
                    "What is the difference between synchronous and asynchronous code?"
                ],
                "advanced": [
                    "How does the JavaScript event loop work?",
                    "Explain prototypal inheritance in JavaScript.",
                    "How would you implement a Promise from scratch?"
                ]
            },
            "react": {
                "basic": [
                    "What is the difference between state and props in React?",
                    "Explain the concept of JSX.",
                    "What are React components and how do you create them?"
                ],
                "intermediate": [
                    "How do React hooks work and why were they introduced?",
                    "Explain the component lifecycle methods in React.",
                    "What is the virtual DOM and how does it improve performance?"
                ],
                "advanced": [
                    "How would you optimize a React application for better performance?",
                    "Explain React's reconciliation algorithm.",
                    "How do you implement code splitting in React?"
                ]
            },
            "node.js": {
                "basic": [
                    "What is Node.js and how does it differ from browser JavaScript?",
                    "Explain the concept of modules in Node.js.",
                    "What is npm and how do you manage dependencies?"
                ],
                "intermediate": [
                    "How does the Node.js event loop work?",
                    "Explain the difference between synchronous and asynchronous operations.",
                    "How do you handle errors in Node.js applications?"
                ],
                "advanced": [
                    "How would you scale a Node.js application?",
                    "Explain cluster and worker threads in Node.js.",
                    "How do you implement caching strategies in Node.js?"
                ]
            },
            "java": {
                "basic": [
                    "What is the difference between abstract classes and interfaces in Java?",
                    "Explain the concept of inheritance in Java.",
                    "What are the different access modifiers in Java?"
                ],
                "intermediate": [
                    "How does garbage collection work in Java?",
                    "Explain the concept of polymorphism with examples.",
                    "What are generics in Java and why are they useful?"
                ],
                "advanced": [
                    "How do you optimize Java applications for better performance?",
                    "Explain the Java memory model and its implications.",
                    "How would you implement a custom thread pool in Java?"
                ]
            },
            "sql": {
                "basic": [
                    "What is the difference between INNER JOIN and LEFT JOIN?",
                    "Explain the concept of primary keys and foreign keys.",
                    "What are the different types of SQL commands?"
                ],
                "intermediate": [
                    "How do you optimize slow-running SQL queries?",
                    "Explain database normalization and its benefits.",
                    "What are indexes and how do they improve performance?"
                ],
                "advanced": [
                    "How would you design a database schema for a complex application?",
                    "Explain ACID properties in database transactions.",
                    "How do you handle database concurrency and locking?"
                ]
            },
            "mongodb": {
                "basic": [
                    "What is MongoDB and how does it differ from relational databases?",
                    "Explain the concept of documents and collections.",
                    "How do you perform basic CRUD operations in MongoDB?"
                ],
                "intermediate": [
                    "How do you design efficient MongoDB schemas?",
                    "Explain indexing strategies in MongoDB.",
                    "What are aggregation pipelines and how do you use them?"
                ],
                "advanced": [
                    "How would you implement sharding in MongoDB?",
                    "Explain replica sets and their role in high availability.",
                    "How do you optimize MongoDB performance?"
                ]
            },
            "docker": {
                "basic": [
                    "What is Docker and what problems does it solve?",
                    "Explain the difference between Docker images and containers.",
                    "How do you create a basic Dockerfile?"
                ],
                "intermediate": [
                    "How do you manage multi-container applications with Docker Compose?",
                    "Explain Docker networking and volume management.",
                    "What are the best practices for writing Dockerfiles?"
                ],
                "advanced": [
                    "How would you implement a CI/CD pipeline with Docker?",
                    "Explain Docker orchestration with Kubernetes.",
                    "How do you optimize Docker images for production?"
                ]
            },
            "kubernetes": {
                "basic": [
                    "What is Kubernetes and what problems does it solve?",
                    "Explain the concept of pods, services, and deployments.",
                    "How do you deploy an application to Kubernetes?"
                ],
                "intermediate": [
                    "How does Kubernetes handle service discovery and load balancing?",
                    "Explain ConfigMaps and Secrets in Kubernetes.",
                    "What are the different types of Kubernetes services?"
                ],
                "advanced": [
                    "How would you implement auto-scaling in Kubernetes?",
                    "Explain Kubernetes networking and ingress controllers.",
                    "How do you monitor and troubleshoot Kubernetes clusters?"
                ]
            }
        }
        
        # Try to find questions for the exact technology
        if tech_lower in tech_questions:
            questions_by_difficulty = tech_questions[tech_lower].get(difficulty, [])
            if questions_by_difficulty:
                # Rotate through questions based on question number
                question_index = (question_number - 1) % len(questions_by_difficulty)
                return questions_by_difficulty[question_index]
        
        # Try partial matches for frameworks/variations
        for key in tech_questions:
            if key in tech_lower or tech_lower in key:
                questions_by_difficulty = tech_questions[key].get(difficulty, [])
                if questions_by_difficulty:
                    question_index = (question_number - 1) % len(questions_by_difficulty)
                    return questions_by_difficulty[question_index]
        
        # Generic programming questions if no specific match
        generic_questions = {
            "basic": [
                f"What are the fundamental concepts you should know when working with {technology}?",
                f"How would you explain {technology} to someone who's new to it?",
                f"What are the main advantages of using {technology} in development?"
            ],
            "intermediate": [
                f"What are some best practices when developing with {technology}?",
                f"How would you debug common issues in {technology} applications?",
                f"What are the performance considerations when using {technology}?"
            ],
            "advanced": [
                f"How would you architect a large-scale application using {technology}?",
                f"What are the advanced features of {technology} that you've worked with?",
                f"How would you optimize and scale applications built with {technology}?"
            ]
        }
        
        questions = generic_questions.get(difficulty, generic_questions["intermediate"])
        question_index = (question_number - 1) % len(questions)
        return questions[question_index]
    
    def get_cached_questions(self) -> Dict[str, str]:
        """Return all cached questions."""
        return self.question_cache.copy()
    
    def clear_cache(self) -> None:
        """Clear the question cache."""
        self.question_cache.clear()