"""
Authentication Service
~~~~~~~~~~~~~~~~~~~~~~

Manages user authentication and session handling.
Provides secure authentication without modifying database state.
"""

import uuid
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from app.models.session import UserSession, session_store
from app.services.training_service import TrainingService


class AuthService:
    """
    Service class for authentication operations.
    
    Handles user authentication, session management, and CISO identification.
    Uses in-memory session storage for stateful authentication.
    """
    
    # CISO employee ID (in production, use role-based system)
    CISO_EMPLOYEE_ID = "123456789"
    
    def __init__(self, db: Session):
        """
        Initialize authentication service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.training_service = TrainingService(db)
    
    def create_session(self) -> str:
        """
        Create a new session.
        
        Returns:
            Session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        session_store.create_session(session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            UserSession if found and valid, None otherwise
        """
        return session_store.get_session(session_id)
    
    def authenticate_employee(
        self,
        session_id: str,
        employee_id: Optional[int] = None,
        employee_name: Optional[str] = None
    ) -> Tuple[bool, str, Optional[UserSession]]:
        """
        Authenticate an employee.
        
        Supports partial authentication (can provide ID or name separately).
        Returns success status, message, and updated session.
        
        Args:
            session_id: Session identifier
            employee_id: Employee ID (optional)
            employee_name: Employee name (optional)
            
        Returns:
            Tuple of (success, message, session)
        """
        session = session_store.get_session(session_id)
        if not session:
            return False, "Invalid session", None
        
        # Update session with provided credentials
        if employee_id is not None:
            session_store.update_session(session_id, employee_id=employee_id)
        if employee_name is not None:
            session_store.update_session(session_id, employee_name=employee_name)
        
        # Get updated session
        session = session_store.get_session(session_id)
        
        # Check if fully authenticated
        if session and session.is_authenticated():
            # Verify credentials against database
            is_valid, employee = self.training_service.verify_employee_credentials(
                session.employee_id,
                session.employee_name
            )
            
            if is_valid:
                # Check if this employee is the CISO based on their ID from the database
                is_ciso = (str(session.employee_id).zfill(9) == self.CISO_EMPLOYEE_ID)
                session_store.update_session(session_id, is_ciso=is_ciso)
                session = session_store.get_session(session_id)
                
                success_msg = "CISO authenticated successfully" if is_ciso else "Authentication successful"
                return True, success_msg, session
            else:
                # Invalid credentials - reset session
                session_store.update_session(
                    session_id,
                    employee_id=None,
                    employee_name=None
                )
                return False, "Invalid credentials. Employee ID and name do not match.", None
        else:
            # Partially authenticated - ask for missing fields
            missing = session.get_missing_fields()
            missing_str = " and ".join(missing)
            return False, f"Please provide your {missing_str}", session
    
    def is_authenticated(self, session_id: str) -> bool:
        """
        Check if session is fully authenticated.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if authenticated, False otherwise
        """
        session = session_store.get_session(session_id)
        return session is not None and session.is_authenticated()
    
    def is_ciso(self, session_id: str) -> bool:
        """
        Check if session belongs to CISO.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if CISO, False otherwise
        """
        session = session_store.get_session(session_id)
        return session is not None and session.is_ciso
    
    def get_authenticated_employee_id(self, session_id: str) -> Optional[int]:
        """
        Get authenticated employee ID from session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Employee ID if authenticated, None otherwise
        """
        session = session_store.get_session(session_id)
        if session and session.is_authenticated():
            return session.employee_id
        return None
    
    def logout(self, session_id: str) -> None:
        """
        Logout and destroy session.
        
        Args:
            session_id: Session identifier
        """
        session_store.delete_session(session_id)

