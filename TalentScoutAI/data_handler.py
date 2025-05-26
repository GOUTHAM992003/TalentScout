import json
import os
import datetime
from typing import Dict, List, Any, Optional
import re

class DataHandler:
    """
    Handles candidate data storage and privacy compliance.
    Implements GDPR-compliant data handling practices.
    """
    
    def __init__(self):
        self.data_directory = "candidate_data"
        self.ensure_data_directory()
        
        # Privacy settings
        self.data_retention_days = 90  # GDPR compliance
        self.anonymization_enabled = True
        
    def ensure_data_directory(self) -> None:
        """Ensure the data directory exists."""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
    
    def save_candidate_data(self, candidate_data: Dict[str, Any]) -> bool:
        """
        Save candidate data with privacy compliance.
        
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
            
            # Create anonymized copy for storage
            stored_data = self._prepare_data_for_storage(candidate_data)
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            candidate_id = self._generate_candidate_id(candidate_data)
            filename = f"candidate_{candidate_id}_{timestamp}.json"
            filepath = os.path.join(self.data_directory, filename)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(stored_data, f, indent=2, ensure_ascii=False)
            
            print(f"Candidate data saved successfully: {filename}")
            
            # Clean old files if needed
            self._cleanup_old_data()
            
            return True
            
        except Exception as e:
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
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            print("Invalid email format")
            return False
        
        # Validate phone if provided
        if 'phone' in data and data['phone']:
            phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)]{8,15}$'
            if not re.match(phone_pattern, data['phone']):
                print("Invalid phone format")
                return False
        
        return True
    
    def _prepare_data_for_storage(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare candidate data for storage with privacy considerations.
        
        Args:
            candidate_data: Raw candidate data
            
        Returns:
            Data prepared for storage with privacy measures applied
        """
        
        stored_data = candidate_data.copy()
        
        # Add metadata
        stored_data['_metadata'] = {
            'timestamp': datetime.datetime.now().isoformat(),
            'data_retention_until': (
                datetime.datetime.now() + datetime.timedelta(days=self.data_retention_days)
            ).isoformat(),
            'privacy_policy_version': '1.0',
            'gdpr_compliance': True,
            'source': 'TalentScout_Chatbot'
        }
        
        # Pseudonymize sensitive data if enabled
        if self.anonymization_enabled:
            stored_data = self._pseudonymize_data(stored_data)
        
        return stored_data
    
    def _pseudonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply pseudonymization to sensitive data fields.
        
        Args:
            data: Original data dictionary
            
        Returns:
            Data with pseudonymized sensitive fields
        """
        
        pseudonymized = data.copy()
        
        # Hash phone number if present (keep format for validation)
        if 'phone' in pseudonymized and pseudonymized['phone']:
            phone = pseudonymized['phone']
            # Keep country code and last 4 digits visible
            if len(phone) > 6:
                visible_part = phone[-4:]
                hidden_part = '*' * (len(phone) - 4)
                pseudonymized['phone_masked'] = hidden_part + visible_part
                pseudonymized['phone_hash'] = str(hash(phone))
                del pseudonymized['phone']  # Remove original
        
        # Partial email masking
        if 'email' in pseudonymized and pseudonymized['email']:
            email = pseudonymized['email']
            username, domain = email.split('@')
            if len(username) > 2:
                masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
                pseudonymized['email_masked'] = f"{masked_username}@{domain}"
                pseudonymized['email_hash'] = str(hash(email))
                # Keep original for business purposes (recruitment contact)
                # In production, consider additional encryption
        
        return pseudonymized
    
    def _generate_candidate_id(self, candidate_data: Dict[str, Any]) -> str:
        """Generate a unique candidate identifier."""
        
        # Create ID based on email hash for consistency
        email = candidate_data.get('email', '')
        name = candidate_data.get('name', '')
        
        # Simple hash-based ID (in production, use proper UUID)
        combined = f"{email}{name}".lower().replace(' ', '')
        candidate_id = str(abs(hash(combined)))[:8]
        
        return candidate_id
    
    def _cleanup_old_data(self) -> None:
        """Remove data files older than retention period."""
        
        try:
            current_time = datetime.datetime.now()
            retention_limit = current_time - datetime.timedelta(days=self.data_retention_days)
            
            for filename in os.listdir(self.data_directory):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.data_directory, filename)
                    
                    # Check file modification time
                    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_time < retention_limit:
                        os.remove(filepath)
                        print(f"Removed expired data file: {filename}")
                        
        except Exception as e:
            print(f"Error during data cleanup: {str(e)}")
    
    def get_candidate_summary(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve candidate summary by ID (for administrative purposes).
        
        Args:
            candidate_id: The candidate identifier
            
        Returns:
            Candidate summary or None if not found
        """
        
        try:
            for filename in os.listdir(self.data_directory):
                if filename.startswith(f"candidate_{candidate_id}") and filename.endswith('.json'):
                    filepath = os.path.join(self.data_directory, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Return summary without sensitive details
                    summary = {
                        'candidate_id': candidate_id,
                        'name': data.get('name', 'N/A'),
                        'position': data.get('position', 'N/A'),
                        'experience': data.get('experience', 'N/A'),
                        'tech_stack': data.get('tech_stack', []),
                        'timestamp': data.get('_metadata', {}).get('timestamp', 'N/A')
                    }
                    
                    return summary
            
            return None
            
        except Exception as e:
            print(f"Error retrieving candidate summary: {str(e)}")
            return None
    
    def export_candidate_data(self, candidate_id: str, export_format: str = 'json') -> Optional[str]:
        """
        Export candidate data for GDPR data portability compliance.
        
        Args:
            candidate_id: The candidate identifier
            export_format: Export format ('json' or 'txt')
            
        Returns:
            Exported data as string or None if not found
        """
        
        try:
            candidate_data = self.get_candidate_summary(candidate_id)
            
            if not candidate_data:
                return None
            
            if export_format.lower() == 'json':
                return json.dumps(candidate_data, indent=2)
            elif export_format.lower() == 'txt':
                lines = []
                lines.append("=== CANDIDATE DATA EXPORT ===")
                lines.append(f"Candidate ID: {candidate_data['candidate_id']}")
                lines.append(f"Name: {candidate_data['name']}")
                lines.append(f"Position: {candidate_data['position']}")
                lines.append(f"Experience: {candidate_data['experience']}")
                lines.append(f"Tech Stack: {', '.join(candidate_data['tech_stack'])}")
                lines.append(f"Date: {candidate_data['timestamp']}")
                lines.append("================================")
                return '\n'.join(lines)
            
            return None
            
        except Exception as e:
            print(f"Error exporting candidate data: {str(e)}")
            return None
    
    def delete_candidate_data(self, candidate_id: str) -> bool:
        """
        Delete candidate data for GDPR right to erasure compliance.
        
        Args:
            candidate_id: The candidate identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        
        try:
            deleted_files = 0
            
            for filename in os.listdir(self.data_directory):
                if filename.startswith(f"candidate_{candidate_id}") and filename.endswith('.json'):
                    filepath = os.path.join(self.data_directory, filename)
                    os.remove(filepath)
                    deleted_files += 1
                    print(f"Deleted candidate data file: {filename}")
            
            return deleted_files > 0
            
        except Exception as e:
            print(f"Error deleting candidate data: {str(e)}")
            return False
