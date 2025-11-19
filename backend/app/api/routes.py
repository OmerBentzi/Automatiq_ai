"""
API Routes
~~~~~~~~~~

FastAPI endpoints for the training assistant.
Implements all required API functionality with proper error handling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.services.training_service import TrainingService
from app.agents.training_agent import TrainingAgent
from app.api.schemas import (
    AuthRequest,
    AuthResponse,
    ChatRequest,
    ChatResponse,
    EmployeeStatusRequest,
    EmployeeStatusResponse,
    GlobalStatusRequest,
    GlobalStatusResponse,
    SessionCreateResponse,
)


router = APIRouter()


@router.post("/session/create", response_model=SessionCreateResponse)
def create_session(db: Session = Depends(get_db)) -> SessionCreateResponse:
    """
    Create a new session.
    
    Returns:
        Session ID and welcome message
    """
    auth_service = AuthService(db)
    session_id = auth_service.create_session()
    
    return SessionCreateResponse(
        session_id=session_id,
        message="Session created successfully. Please authenticate with your employee ID and name."
    )


@router.post("/authenticate", response_model=AuthResponse)
def authenticate(
    request: AuthRequest,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """
    Authenticate a user with employee ID and/or name.
    
    Supports partial authentication - can provide ID or name separately.
    
    Args:
        request: Authentication request with session_id and credentials
        db: Database session
        
    Returns:
        Authentication result with status
    """
    auth_service = AuthService(db)
    
    # Authenticate with provided credentials
    success, message, session = auth_service.authenticate_employee(
        request.session_id,
        request.employee_id,
        request.employee_name
    )
    
    # Build response
    is_authenticated = session.is_authenticated() if session else False
    is_ciso = session.is_ciso if session else False
    missing_fields = session.get_missing_fields() if session and not is_authenticated else []
    
    return AuthResponse(
        success=success,
        message=message,
        session_id=request.session_id,
        is_authenticated=is_authenticated,
        is_ciso=is_ciso,
        missing_fields=missing_fields
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Process a natural language query about training.
    
    The agent will:
    1. Validate the query through guardrails
    2. Check authentication
    3. Parse intent
    4. Retrieve relevant data
    5. Generate natural language response
    
    Args:
        request: Chat request with query and session_id
        db: Database session
        
    Returns:
        AI-generated response with context data
    """
    try:
        agent = TrainingAgent(db)
        result = agent.process_query(request.query, request.session_id)
        
        return ChatResponse(
            success=result["success"],
            response=result["response"],
            intent=result.get("intent"),
            requires_auth=result.get("requires_auth", False),
            context_data=result.get("context_data")
        )
    
    except Exception as e:
        return ChatResponse(
            success=False,
            response=f"An error occurred while processing your query. Please try again.",
            requires_auth=False
        )


@router.post("/status/employee", response_model=EmployeeStatusResponse)
def get_employee_status(
    request: EmployeeStatusRequest,
    db: Session = Depends(get_db)
) -> EmployeeStatusResponse:
    """
    Get detailed status for a specific employee.
    
    Regular employees can only view their own status.
    CISO can view any employee's status by providing employee_id.
    
    Args:
        request: Status request with session_id and optional employee_id
        db: Database session
        
    Returns:
        Employee status details
    """
    try:
        auth_service = AuthService(db)
        training_service = TrainingService(db)
        
        # Check authentication
        if not auth_service.is_authenticated(request.session_id):
            return EmployeeStatusResponse(
                success=False,
                error="Not authenticated. Please authenticate first."
            )
        
        # Determine which employee to query
        if request.employee_id:
            # CISO querying specific employee
            if not auth_service.is_ciso(request.session_id):
                return EmployeeStatusResponse(
                    success=False,
                    error="You don't have permission to view other employees' status."
                )
            employee_id = request.employee_id
        else:
            # User querying their own status
            employee_id = auth_service.get_authenticated_employee_id(request.session_id)
        
        # Get status
        status_data = training_service.get_employee_status(employee_id)
        
        if "error" in status_data:
            return EmployeeStatusResponse(
                success=False,
                error=status_data["error"]
            )
        
        return EmployeeStatusResponse(
            success=True,
            data=status_data
        )
    
    except Exception as e:
        return EmployeeStatusResponse(
            success=False,
            error="An error occurred while retrieving status."
        )


@router.post("/status/all", response_model=GlobalStatusResponse)
def get_global_status(
    request: GlobalStatusRequest,
    db: Session = Depends(get_db)
) -> GlobalStatusResponse:
    """
    Get global training statistics (CISO only).
    
    Provides:
    - If status_filter provided: List of employees with that status
    - Otherwise: Global summary with aggregated statistics
    
    Args:
        request: Global status request with session_id and optional filter
        db: Database session
        
    Returns:
        Global statistics or filtered employee list
    """
    try:
        auth_service = AuthService(db)
        training_service = TrainingService(db)
        
        # Check authentication
        if not auth_service.is_authenticated(request.session_id):
            return GlobalStatusResponse(
                success=False,
                error="Not authenticated. Please authenticate first."
            )
        
        # Check CISO permission
        if not auth_service.is_ciso(request.session_id):
            return GlobalStatusResponse(
                success=False,
                error="CISO access required for global statistics."
            )
        
        # Get data based on filter
        if request.status_filter:
            # Validate status
            valid_statuses = ["NOT_STARTED", "IN_PROGRESS", "FINISHED"]
            if request.status_filter not in valid_statuses:
                return GlobalStatusResponse(
                    success=False,
                    error=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )
            
            # Get employees by status
            employees = training_service.get_employees_by_status(request.status_filter)
            data = {
                "status_filter": request.status_filter,
                "employees": employees,
                "count": len(employees)
            }
        else:
            # Get global summary
            data = training_service.get_global_summary()
        
        return GlobalStatusResponse(
            success=True,
            data=data
        )
    
    except Exception as e:
        return GlobalStatusResponse(
            success=False,
            error="An error occurred while retrieving global statistics."
        )


@router.get("/health")
def health_check() -> Dict:
    """
    Health check endpoint.
    
    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "CyberSecurity Training Assistant",
        "version": "1.0.0"
    }

