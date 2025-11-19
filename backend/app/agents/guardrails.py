"""
Guardrails Module
~~~~~~~~~~~~~~~~~

Implements safety guardrails to prevent harmful or off-topic interactions.
Ensures the agent only responds to cybersecurity training-related queries.
"""

import re
from typing import Tuple, List


class Guardrails:
    """
    Guardrails class for filtering and validating user inputs.
    
    Implements multiple layers of protection:
    1. Topic validation - only training-related topics
    2. Command injection prevention - block harmful SQL/system commands
    3. Data modification prevention - block UPDATE/DELETE/INSERT operations
    4. Prompt injection prevention - detect and block manipulation attempts
    """
    
    # Keywords related to cybersecurity training (allowed)
    ALLOWED_TOPICS = [
        "training", "video", "course", "completed", "finished", "status",
        "progress", "cybersecurity", "security", "phishing", "password",
        "data protection", "incident", "response", "employee", "learning",
        "certification", "module", "lesson", "duration", "time", "hours",
        "minutes", "started", "completion", "percentage", "ciso", "department"
    ]
    
    # Forbidden keywords (not allowed)
    FORBIDDEN_KEYWORDS = [
        # Database manipulation
        "update", "delete", "insert", "drop", "alter", "truncate", "create",
        "modify", "change", "set", "exec", "execute",
        # System commands
        "system", "shell", "cmd", "bash", "powershell", "eval", "compile",
        # Sensitive operations
        "password=", "credential", "api_key", "secret", "token",
        # Prompt injection attempts
        "ignore previous", "ignore instructions", "ignore prompt",
        "new instructions", "system prompt", "override",
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|from|where)\b.*\b(select|from|where)\b)",
        r"(;|\-\-|\/\*|\*\/)",
        r"(\b(or|and)\b.*[=<>].*['\"])",
        r"(drop\s+table)",
        r"(delete\s+from)",
        r"(update\s+\w+\s+set)",
    ]
    
    @classmethod
    def is_training_related(cls, query: str) -> Tuple[bool, str]:
        """
        Check if query is related to cybersecurity training.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (is_related, reason)
        """
        query_lower = query.lower()
        
        # Check for allowed topics
        has_allowed_topic = any(
            keyword in query_lower for keyword in cls.ALLOWED_TOPICS
        )
        
        # If no allowed topics found, it might be off-topic
        if not has_allowed_topic and len(query.split()) > 3:
            return False, "This query appears to be unrelated to cybersecurity training. Please ask about training videos, completion status, or employee progress."
        
        return True, ""
    
    @classmethod
    def check_forbidden_keywords(cls, query: str) -> Tuple[bool, str]:
        """
        Check for forbidden keywords that might indicate harmful intent.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (is_safe, reason)
        """
        query_lower = query.lower()
        
        for keyword in cls.FORBIDDEN_KEYWORDS:
            if keyword in query_lower:
                return False, f"This query contains forbidden operations. I can only provide read-only information about training status."
        
        return True, ""
    
    @classmethod
    def check_sql_injection(cls, query: str) -> Tuple[bool, str]:
        """
        Check for SQL injection patterns.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (is_safe, reason)
        """
        query_lower = query.lower()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False, "Invalid query format detected. Please use natural language questions."
        
        return True, ""
    
    @classmethod
    def validate_query(cls, query: str) -> Tuple[bool, str]:
        """
        Comprehensive query validation through all guardrails.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Empty query check
        if not query or not query.strip():
            return False, "Please provide a query."
        
        # Length check
        if len(query) > 1000:
            return False, "Query is too long. Please keep questions concise."
        
        # SQL injection check
        is_safe, reason = cls.check_sql_injection(query)
        if not is_safe:
            return False, reason
        
        # Forbidden keywords check
        is_safe, reason = cls.check_forbidden_keywords(query)
        if not is_safe:
            return False, reason
        
        # Topic relevance check
        is_relevant, reason = cls.is_training_related(query)
        if not is_relevant:
            return False, reason
        
        return True, ""
    
    @classmethod
    def sanitize_response(cls, response: str) -> str:
        """
        Sanitize AI response to remove any potentially harmful content.
        
        Args:
            response: AI-generated response
            
        Returns:
            Sanitized response
        """
        # Remove any accidentally leaked system prompts or instructions
        sanitized = response
        
        # Remove common instruction patterns
        patterns_to_remove = [
            r"\[SYSTEM\].*?\[/SYSTEM\]",
            r"<system>.*?</system>",
            r"```sql.*?```",
        ]
        
        for pattern in patterns_to_remove:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        return sanitized.strip()
    
    @classmethod
    def get_rejection_message(cls) -> str:
        """
        Get standard rejection message for off-topic queries.
        
        Returns:
            Rejection message
        """
        return (
            "I can only answer questions about cybersecurity training. "
            "Please ask about:\n"
            "- Training completion status\n"
            "- Video progress and duration\n"
            "- Employee training statistics\n"
            "- CISO reports and summaries"
        )

