"""
API Tests
~~~~~~~~~

Tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_session(client: TestClient):
    """Test session creation"""
    response = client.post("/api/session/create")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0


def test_authenticate_employee(client: TestClient):
    """Test employee authentication"""
    # Create session
    session_response = client.post("/api/session/create")
    session_id = session_response.json()["session_id"]
    
    # Authenticate
    auth_response = client.post(
        "/api/authenticate",
        json={
            "session_id": session_id,
            "employee_id": 1,
            "employee_name": "John Doe"
        }
    )
    
    assert auth_response.status_code == 200
    data = auth_response.json()
    assert data["success"] is True
    assert data["is_authenticated"] is True


def test_authenticate_partial(client: TestClient):
    """Test partial authentication"""
    # Create session
    session_response = client.post("/api/session/create")
    session_id = session_response.json()["session_id"]
    
    # Provide only ID
    auth_response = client.post(
        "/api/authenticate",
        json={
            "session_id": session_id,
            "employee_id": 1
        }
    )
    
    assert auth_response.status_code == 200
    data = auth_response.json()
    assert data["success"] is False
    assert data["is_authenticated"] is False
    assert "employee_name" in data["missing_fields"]


def test_chat_without_auth(client: TestClient):
    """Test chat without authentication"""
    # Create session
    session_response = client.post("/api/session/create")
    session_id = session_response.json()["session_id"]
    
    # Try to chat without auth
    chat_response = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "query": "What is my training status?"
        }
    )
    
    assert chat_response.status_code == 200
    data = chat_response.json()
    assert data["requires_auth"] is True


def test_chat_with_auth(client: TestClient):
    """Test chat with authentication"""
    # Create session
    session_response = client.post("/api/session/create")
    session_id = session_response.json()["session_id"]
    
    # Authenticate
    client.post(
        "/api/authenticate",
        json={
            "session_id": session_id,
            "employee_id": 1,
            "employee_name": "John Doe"
        }
    )
    
    # Chat
    chat_response = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "query": "What videos have I completed?"
        }
    )
    
    assert chat_response.status_code == 200
    data = chat_response.json()
    assert data["success"] is True
    assert "response" in data


def test_employee_status(client: TestClient):
    """Test employee status endpoint"""
    # Create session and authenticate
    session_response = client.post("/api/session/create")
    session_id = session_response.json()["session_id"]
    
    client.post(
        "/api/authenticate",
        json={
            "session_id": session_id,
            "employee_id": 1,
            "employee_name": "John Doe"
        }
    )
    
    # Get status
    status_response = client.post(
        "/api/status/employee",
        json={"session_id": session_id}
    )
    
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["success"] is True
    assert data["data"]["employee_id"] == 1
    assert data["data"]["completion_percentage"] == 40.0

