"""
API Schemas
~~~~~~~~~~~

Pydantic models for request/response validation.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    """Authentication request schema"""
    session_id: str = Field(..., description="Session identifier")
    employee_id: Optional[int] = Field(None, description="Employee ID")
    employee_name: Optional[str] = Field(None, description="Employee name")


class AuthResponse(BaseModel):
    """Authentication response schema"""
    success: bool
    message: str
    session_id: str
    is_authenticated: bool
    is_ciso: bool = False
    missing_fields: List[str] = []


class ChatRequest(BaseModel):
    """Chat request schema"""
    query: str = Field(..., description="User's natural language question")
    session_id: str = Field(..., description="Session identifier")


class ChatResponse(BaseModel):
    """Chat response schema"""
    success: bool
    response: str
    intent: Optional[str] = None
    requires_auth: bool = False
    context_data: Optional[Dict[str, Any]] = None


class EmployeeStatusRequest(BaseModel):
    """Employee status request schema"""
    session_id: str = Field(..., description="Session identifier")
    employee_id: Optional[int] = Field(None, description="Employee ID (CISO only)")


class EmployeeStatusResponse(BaseModel):
    """Employee status response schema"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class GlobalStatusRequest(BaseModel):
    """Global status request schema"""
    session_id: str = Field(..., description="Session identifier")
    status_filter: Optional[str] = Field(
        None,
        description="Status filter: NOT_STARTED, IN_PROGRESS, or FINISHED"
    )


class GlobalStatusResponse(BaseModel):
    """Global status response schema"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SessionCreateResponse(BaseModel):
    """Session creation response schema"""
    session_id: str
    message: str

