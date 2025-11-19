"""
User Session Model
~~~~~~~~~~~~~~~~~~

In-memory session management for authenticated users.
Stores session state without modifying the database.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from pydantic import BaseModel
from app.core.config import settings


class UserSession(BaseModel):
    """
    User session model for managing authentication state.
    
    This is an in-memory model (not stored in database) that tracks
    the authentication state of users during their interaction with the system.
    
    Attributes:
        session_id: Unique session identifier
        employee_id: Authenticated employee ID
        employee_name: Authenticated employee name
        is_ciso: Whether user is authenticated as CISO
        created_at: Session creation timestamp
        last_activity: Last activity timestamp
        metadata: Additional session metadata
    """
    
    session_id: str
    employee_id: Optional[int] = None
    employee_name: Optional[str] = None
    is_ciso: bool = False
    created_at: datetime = datetime.utcnow()
    last_activity: datetime = datetime.utcnow()
    metadata: Dict = {}
    
    def is_authenticated(self) -> bool:
        """
        Check if session is fully authenticated.
        
        Returns:
            True if both employee_id and employee_name are set
        """
        return self.employee_id is not None and self.employee_name is not None
    
    def is_expired(self) -> bool:
        """
        Check if session has expired.
        
        Returns:
            True if session has exceeded timeout period
        """
        timeout = timedelta(minutes=settings.session_timeout_minutes)
        return datetime.utcnow() - self.last_activity > timeout
    
    def update_activity(self) -> None:
        """Update last activity timestamp to current time"""
        self.last_activity = datetime.utcnow()
    
    def get_missing_fields(self) -> list[str]:
        """
        Get list of required fields that are still missing.
        
        Returns:
            List of field names that need to be provided
        """
        missing = []
        if self.employee_id is None:
            missing.append("employee_id")
        if self.employee_name is None:
            missing.append("employee_name")
        return missing
    
    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True


# In-memory session store (in production, use Redis or similar)
class SessionStore:
    """
    In-memory session storage.
    
    In production, this should be replaced with Redis or a similar
    distributed cache to support multiple backend instances.
    """
    
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
    
    def create_session(self, session_id: str) -> UserSession:
        """
        Create a new session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            New UserSession instance
        """
        session = UserSession(session_id=session_id)
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            UserSession if found, None otherwise
        """
        session = self._sessions.get(session_id)
        if session and session.is_expired():
            # Remove expired session
            del self._sessions[session_id]
            return None
        return session
    
    def update_session(self, session_id: str, **kwargs) -> Optional[UserSession]:
        """
        Update session attributes.
        
        Args:
            session_id: Session identifier
            **kwargs: Attributes to update
            
        Returns:
            Updated UserSession if found, None otherwise
        """
        session = self.get_session(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.update_activity()
            self._sessions[session_id] = session
        return session
    
    def delete_session(self, session_id: str) -> None:
        """
        Delete session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions.
        
        Returns:
            Number of sessions removed
        """
        expired = [
            sid for sid, session in self._sessions.items()
            if session.is_expired()
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)


# Global session store instance
session_store = SessionStore()

