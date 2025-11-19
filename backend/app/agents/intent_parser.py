"""
Intent Parser Module
~~~~~~~~~~~~~~~~~~~~

Analyzes natural language queries to determine user intent.
Routes queries to appropriate database operations.
"""

import re
from typing import Dict, Optional, List
from enum import Enum


class Intent(Enum):
    """Enumeration of possible user intents"""
    CHECK_COMPLETION = "check_completion"
    LIST_MISSING_VIDEOS = "list_missing_videos"
    LIST_COMPLETED_VIDEOS = "list_completed_videos"
    VIDEO_DURATION = "video_duration"
    EMPLOYEE_STATUS = "employee_status"
    GLOBAL_SUMMARY = "global_summary"
    LIST_BY_STATUS = "list_by_status"
    LIST_BY_VIDEO_COUNT = "list_by_video_count"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"


class IntentParser:
    """
    Natural language intent parser.
    
    Analyzes user queries to determine what information they're seeking.
    Uses keyword matching and pattern recognition for intent classification.
    """
    
    # Intent patterns (keyword-based)
    INTENT_PATTERNS = {
        Intent.CHECK_COMPLETION: [
            r"\b(did|have|has|completed|finished|done)\b.*\b(training|videos?|courses?)\b",
            r"\b(training|videos?|courses?)\b.*\b(completed?|finished|done)\b",
            r"\b(finished|completed)\b.*\b(all|everything)\b",
        ],
        Intent.LIST_MISSING_VIDEOS: [
            r"\b(what|which|list)\b.*\b(missing|not completed?|remaining|left)\b.*\b(videos?)\b",
            r"\b(videos?)\b.*\b(missing|not completed?|remaining|left)\b",
            r"\b(haven't|have not|didn't|did not)\b.*\b(complete|finish|watch)\b",
            r"\b(need to|have to|must)\b.*\b(complete|finish|watch)\b",
        ],
        Intent.LIST_COMPLETED_VIDEOS: [
            r"\b(what|which|list)\b.*\b(completed?|finished|done|watched)\b.*\b(videos?)\b",
            r"\b(videos?)\b.*\b(completed?|finished|done|watched)\b",
            r"\b(show|tell|give)\b.*\b(completed?|finished)\b",
        ],
        Intent.VIDEO_DURATION: [
            r"\b(how long|duration|time|minutes|hours)\b.*\b(video|spent|took)\b",
            r"\b(video)\b.*\b(duration|time|long)\b",
            r"\b(spent)\b.*\b(video|training)\b",
        ],
        Intent.EMPLOYEE_STATUS: [
            r"\b(status|progress|summary)\b",
            r"\b(what is|show|give|tell)\b.*\b(my|their)\b.*\b(status|progress)\b",
            r"\b(completion|percentage|%)\b",
        ],
        Intent.GLOBAL_SUMMARY: [
            r"\b(all employees|everyone|global|overall|company|organization)\b",
            r"\b(average|mean|statistics|stats|summary)\b.*\b(all|everyone)\b",
            r"\b(fastest|slowest|longest|shortest)\b.*\b(employee)\b",
        ],
        Intent.LIST_BY_STATUS: [
            r"\b(list|show|who)\b.*\b(not started|in progress|finished|completed)\b",
            r"\b(employees?)\b.*\b(not started|in progress|finished|completed)\b",
        ],
        Intent.LIST_BY_VIDEO_COUNT: [
            r"\b(how many|who|list)\b.*\b(completed?|finished|watched)\b.*\b(\d+|two|three|four)\b.*\b(or more|or less|videos?)\b",
            r"\b(employees?|people|users)\b.*\b(\d+|two|three|four)\b.*\b(or more|or less)\b.*\b(videos?)\b",
        ],
    }
    
    @classmethod
    def extract_video_number(cls, query: str) -> Optional[int]:
        """
        Extract video number from query.
        
        Args:
            query: User query
            
        Returns:
            Video number (1-5) if found, None otherwise
        """
        # Look for "video X" or "video number X"
        patterns = [
            r"video\s+(\d+)",
            r"video\s+number\s+(\d+)",
            r"module\s+(\d+)",
            r"lesson\s+(\d+)",
            r"#(\d+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                num = int(match.group(1))
                if 1 <= num <= 5:
                    return num
        
        return None
    
    @classmethod
    def extract_status(cls, query: str) -> Optional[str]:
        """
        Extract status from query.
        
        Args:
            query: User query
            
        Returns:
            Status (NOT_STARTED, IN_PROGRESS, FINISHED) if found, None otherwise
        """
        query_lower = query.lower()
        
        if "not started" in query_lower or "haven't started" in query_lower:
            return "NOT_STARTED"
        elif "in progress" in query_lower or "ongoing" in query_lower or "started" in query_lower:
            return "IN_PROGRESS"
        elif "finished" in query_lower or "completed" in query_lower or "done" in query_lower:
            return "FINISHED"
        
        return None
    
    @classmethod
    def extract_employee_mention(cls, query: str) -> Optional[str]:
        """
        Check if query mentions a specific employee.
        
        Args:
            query: User query
            
        Returns:
            "self" if asking about themselves, "other" if asking about another employee
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["my", "i", "me", "myself"]):
            return "self"
        elif any(word in query_lower for word in ["his", "her", "their", "employee"]):
            return "other"
        
        return "self"  # Default to self
    
    @classmethod
    def extract_employee_name(cls, query: str) -> Optional[str]:
        """
        Extract employee name from query (for CISO queries about specific employees).
        
        Examples:
        - "How many videos did Charlie Levi finish" -> "Charlie Levi"
        - "What is Eli Vardi's status" -> "Eli Vardi"
        - "Show me Nina Hartman progress" -> "Nina Hartman"
        
        Args:
            query: User query
            
        Returns:
            Employee name if found, None otherwise
        """
        import re
        
        # Pattern 1: "did/has/for [Capitalized Name]"
        # Pattern 2: "[Capitalized Name]'s"
        # Pattern 3: "[Capitalized Name] status/progress/training"
        patterns = [
            r'\b(?:did|has|for|about)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\'s',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+(?:status|progress|training|finish)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        
        return None
    
    @classmethod
    def extract_video_count_filter(cls, query: str) -> Optional[Dict[str, any]]:
        """
        Extract video count filter from query.
        
        Examples:
        - "2 or more videos" -> {"count": 2, "operator": ">="}
        - "at least 3 videos" -> {"count": 3, "operator": ">="}
        - "less than 2 videos" -> {"count": 2, "operator": "<"}
        
        Args:
            query: User query
            
        Returns:
            Dictionary with count and operator, or None
        """
        import re
        
        query_lower = query.lower()
        
        # Extract number
        number_match = re.search(r'\b(\d+|one|two|three|four|five)\b', query_lower)
        if not number_match:
            return None
        
        num_str = number_match.group(1)
        word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        count = word_to_num.get(num_str, int(num_str) if num_str.isdigit() else None)
        
        if count is None:
            return None
        
        # Determine operator
        if "or more" in query_lower or "at least" in query_lower:
            operator = ">="
        elif "or less" in query_lower or "at most" in query_lower:
            operator = "<="
        elif "less than" in query_lower or "fewer than" in query_lower:
            operator = "<"
        elif "more than" in query_lower:
            operator = ">"
        elif "exactly" in query_lower:
            operator = "=="
        else:
            operator = ">="  # Default
        
        return {"count": count, "operator": operator}
    
    @classmethod
    def classify_intent(cls, query: str) -> Intent:
        """
        Classify user intent from natural language query.
        
        Args:
            query: User query
            
        Returns:
            Classified intent
        """
        query_lower = query.lower()
        
        # Check each intent pattern
        for intent, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    return intent
        
        # Default to general question
        return Intent.GENERAL_QUESTION
    
    @classmethod
    def parse(cls, query: str) -> Dict:
        """
        Parse query and extract all relevant information.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with intent and extracted parameters
        """
        intent = cls.classify_intent(query)
        
        result = {
            "intent": intent,
            "query": query,
            "video_number": cls.extract_video_number(query),
            "status": cls.extract_status(query),
            "employee_mention": cls.extract_employee_mention(query),
            "employee_name": cls.extract_employee_name(query),
            "video_count_filter": cls.extract_video_count_filter(query),
        }
        
        return result
    
    @classmethod
    def is_ciso_query(cls, query: str) -> bool:
        """
        Determine if query is a CISO-level query (about multiple employees).
        
        Args:
            query: User query
            
        Returns:
            True if CISO query, False otherwise
        """
        query_lower = query.lower()
        
        ciso_keywords = [
            "all employees", "everyone", "global", "overall", "company",
            "organization", "statistics", "report", "summary of all",
            "fastest", "slowest", "average", "list employees"
        ]
        
        return any(keyword in query_lower for keyword in ciso_keywords)

