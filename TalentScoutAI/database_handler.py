import os
import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

class Candidate(Base):
    """Database model for storing candidate information"""
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20))
    experience = Column(String(50))
    position = Column(String(200))
    location = Column(String(200))
    tech_stack = Column(JSON)
    technical_questions = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class DatabaseHandler:
    """
    Handles candidate data storage using PostgreSQL database.
    Implements GDPR-compliant data handling practices.
    """
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not found")
        
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Privacy settings
        self.data_retention_days = 90  # GDPR compliance
    
    def save_candidate_data(self, candidate_data: Dict[str, Any]) -> bool:
        """
        Save candidate data to PostgreSQL database.
        
        Args:
            candidate_data: Dictionary containing candidate information
            
        Returns:
            True if save successful, False otherwise
        """
        
        try:
            # Validate required fields
            if not self._validate_candidate_data(candidate_data):
                print("Warning: Candidate data validation failed")
                return False
            
            # Generate unique candidate ID
            candidate_id = self._generate_candidate_id(candidate_data)
            
            # Check if candidate already exists
            existing = self.session.query(Candidate).filter_by(candidate_id=candidate_id).first()
            
            if existing:
                # Update existing candidate
                existing.name = candidate_data.get('name')
                existing.email = candidate_data.get('email')
                existing.phone = candidate_data.get('phone')
                existing.experience = candidate_data.get('experience')
                existing.position = candidate_data.get('position')
                existing.location = candidate_data.get('location')
                existing.tech_stack = candidate_data.get('tech_stack', [])
                existing.technical_questions = candidate_data.get('technical_questions', [])
                existing.updated_at = datetime.datetime.utcnow()
            else:
                # Create new candidate record
                candidate = Candidate(
                    candidate_id=candidate_id,
                    name=candidate_data.get('name'),
                    email=candidate_data.get('email'),
                    phone=candidate_data.get('phone'),
                    experience=candidate_data.get('experience'),
                    position=candidate_data.get('position'),
                    location=candidate_data.get('location'),
                    tech_stack=candidate_data.get('tech_stack', []),
                    technical_questions=candidate_data.get('technical_questions', [])
                )
                self.session.add(candidate)
            
            self.session.commit()
            print(f"Candidate data saved successfully: {candidate_id}")
            
            # Clean old data if needed
            self._cleanup_old_data()
            
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"Error saving candidate data: {str(e)}")
            return False
    
    def _validate_candidate_data(self, data: Dict[str, Any]) -> bool:
        """Validate candidate data structure and content."""
        
        required_fields = ['name', 'email']
        
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field]:
                print(f"Missing required field: {field}")
                return False
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            print("Invalid email format")
            return False
        
        return True
    
    def _generate_candidate_id(self, candidate_data: Dict[str, Any]) -> str:
        """Generate a unique candidate identifier."""
        
        # Create ID based on email hash for consistency
        email = candidate_data.get('email', '')
        name = candidate_data.get('name', '')
        
        # Simple hash-based ID
        combined = f"{email}{name}".lower().replace(' ', '')
        candidate_id = str(abs(hash(combined)))[:8]
        
        return candidate_id
    
    def _cleanup_old_data(self) -> None:
        """Remove data records older than retention period."""
        
        try:
            retention_limit = datetime.datetime.utcnow() - datetime.timedelta(days=self.data_retention_days)
            
            # Delete old records
            deleted_count = self.session.query(Candidate).filter(
                Candidate.created_at < retention_limit
            ).delete()
            
            if deleted_count > 0:
                self.session.commit()
                print(f"Removed {deleted_count} expired candidate records")
                
        except Exception as e:
            self.session.rollback()
            print(f"Error during data cleanup: {str(e)}")
    
    def get_candidate_summary(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve candidate summary by ID.
        
        Args:
            candidate_id: The candidate identifier
            
        Returns:
            Candidate summary or None if not found
        """
        
        try:
            candidate = self.session.query(Candidate).filter_by(candidate_id=candidate_id).first()
            
            if candidate:
                return {
                    'candidate_id': candidate.candidate_id,
                    'name': candidate.name,
                    'email': candidate.email,
                    'position': candidate.position,
                    'experience': candidate.experience,
                    'tech_stack': candidate.tech_stack or [],
                    'technical_questions': candidate.technical_questions or [],
                    'created_at': candidate.created_at.isoformat() if candidate.created_at else None
                }
            
            return None
            
        except Exception as e:
            print(f"Error retrieving candidate summary: {str(e)}")
            return None
    
    def get_all_candidates(self) -> List[Dict[str, Any]]:
        """
        Retrieve all candidates summary.
        
        Returns:
            List of candidate summaries
        """
        
        try:
            candidates = self.session.query(Candidate).all()
            
            return [{
                'candidate_id': c.candidate_id,
                'name': c.name,
                'email': c.email,
                'position': c.position,
                'experience': c.experience,
                'tech_stack': c.tech_stack or [],
                'created_at': c.created_at.isoformat() if c.created_at else None
            } for c in candidates]
            
        except Exception as e:
            print(f"Error retrieving candidates: {str(e)}")
            return []
    
    def delete_candidate_data(self, candidate_id: str) -> bool:
        """
        Delete candidate data for GDPR right to erasure compliance.
        
        Args:
            candidate_id: The candidate identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        
        try:
            deleted_count = self.session.query(Candidate).filter_by(candidate_id=candidate_id).delete()
            
            if deleted_count > 0:
                self.session.commit()
                print(f"Deleted candidate data: {candidate_id}")
                return True
            else:
                print(f"No candidate found with ID: {candidate_id}")
                return False
            
        except Exception as e:
            self.session.rollback()
            print(f"Error deleting candidate data: {str(e)}")
            return False
    
    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()