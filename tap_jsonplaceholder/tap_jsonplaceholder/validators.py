"""validators.py"""
from typing import Dict, Any, List
import re

class SimpleValidator:
    """Simple validator class for basic data validation."""

    def __init__(self):
        self.errors = []

    def check_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Check if all required fields are present and not None."""
        for field in required_fields:
            if field not in data or data[field] is None:
                self.errors.append(f"Missing required field: {field}")
                return False
        return True

    def check_string_not_empty(self, value: str, field_name: str) -> bool:
        """Check if string is not empty or just whitespace."""
        if not value or value.strip() == "":
            self.errors.append(f"Field {field_name} cannot be empty")
            return False
        return True

    def check_positive_integer(self, value: int, field_name: str) -> bool:
        """Check if value is a positive integer."""
        if not isinstance(value, int) or value <= 0:
            self.errors.append(f"Field {field_name} must be a positive integer")
            return False
        return True

    def check_email_format(self, email: str) -> bool:
        """Basic email format validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            self.errors.append("Invalid email format")
            return False
        return True

class PostValidator(SimpleValidator):
    """Validator for Post records."""

    def validate(self, post: Dict[str, Any]) -> bool:
        """Validate post data."""
        self.errors = []  

       
        required_fields = ['id', 'userId', 'title', 'body']
        if not self.check_required_fields(post, required_fields):
            return False

        
        self.check_positive_integer(post['id'], 'id')
        self.check_positive_integer(post['userId'], 'userId')

        
        self.check_string_not_empty(post['title'], 'title')
        self.check_string_not_empty(post['body'], 'body')

        return len(self.errors) == 0

class CommentValidator(SimpleValidator):
    """Validator for Comment records."""

    def validate(self, comment: Dict[str, Any]) -> bool:
        """Validate comment data."""
        self.errors = []  

       
        required_fields = ['id', 'postId', 'name', 'email', 'body']
        if not self.check_required_fields(comment, required_fields):
            return False

        # Validate ID and postId
        self.check_positive_integer(comment['id'], 'id')
        self.check_positive_integer(comment['postId'], 'postId')

        # Validate strings
        self.check_string_not_empty(comment['name'], 'name')
        self.check_string_not_empty(comment['body'], 'body')

        # Validate email
        self.check_email_format(comment['email'])

        return len(self.errors) == 0

class UserValidator(SimpleValidator):
    """Validator for User records."""

    def validate(self, user: Dict[str, Any]) -> bool:
        """Validate user data."""
        self.errors = []  # Reset errors

        # Check required fields
        required_fields = ['id', 'name', 'username', 'email']
        if not self.check_required_fields(user, required_fields):
            return False

        # Validate ID
        self.check_positive_integer(user['id'], 'id')

        # Validate strings
        self.check_string_not_empty(user['name'], 'name')
        self.check_string_not_empty(user['username'], 'username')

        # Validate email
        self.check_email_format(user['email'])

        return len(self.errors) == 0