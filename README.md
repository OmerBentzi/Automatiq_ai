# CyberSecurity Training Assistant

A production-grade AI-powered assistant for managing and querying company cybersecurity training status. Built with FastAPI, React, TypeScript, and enterprise-level architecture with strict guardrails and security measures.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.3-blue.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Running with Docker](#running-with-docker)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Security & Guardrails](#security--guardrails)
- [Example Scenarios](#example-scenarios)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

##  Overview

The **CyberSecurity Training Assistant** is an intelligent system that helps employees and CISOs manage and query cybersecurity training completion status. It uses natural language processing powered by LLMs (OpenAI GPT-4 or Anthropic Claude) with comprehensive guardrails to ensure safe, read-only operations.

### Key Capabilities

- ✅ **Employee Features**: Check training completion, list missing/completed videos, view time spent
- ✅ **CISO Features**: Company-wide statistics, employee filtering by status, performance analytics
- ✅ **AI-Powered**: Natural language understanding with intent classification
- ✅ **Secure**: Multi-layer guardrails prevent SQL injection, prompt injection, and off-topic queries
- ✅ **Authentication**: Session-based authentication with ID + name verification
- ✅ **Read-Only**: No database modifications allowed, ensuring data integrity

---

##  Features

### 1. Authentication System

- **Two-Factor Authentication**: Requires both Employee ID and Name
- **Session Management**: Stateful sessions with automatic expiration
- **CISO Access**: Special credentials for administrative queries
- **Persistent Sessions**: Survives page refreshes via localStorage

### 2. Employee Features

Users can ask natural language questions like:

- "What is my training status?"
- "Which videos have I completed?"
- "What videos am I missing?"
- "How long did video 3 take me?"
- "Did I finish all training?"

The system provides:
- Current completion percentage
- List of completed/missing videos
- Time spent on each video
- Overall training status (NOT_STARTED, IN_PROGRESS, FINISHED)

### 3. CISO Features

Administrators can query:

- "Show me all employees who finished training"
- "List employees who haven't started"
- "Give me global training statistics"
- "Who is the fastest/slowest employee?"

Provides:
- Global completion statistics
- Employee filtering by status
- Min/max/average completion times
- Fastest and slowest performers

### 4. AI Agent with Guardrails

**Multi-Layer Security:**

1. **Topic Validation**: Only training-related queries accepted
2. **SQL Injection Prevention**: Pattern matching for malicious SQL
3. **Forbidden Keywords**: Blocks UPDATE, DELETE, INSERT, DROP, etc.
4. **Prompt Injection Detection**: Prevents "ignore previous instructions" attacks
5. **Response Sanitization**: Removes potentially harmful content from AI responses

**Intent Classification:**
- CHECK_COMPLETION
- LIST_MISSING_VIDEOS
- LIST_COMPLETED_VIDEOS
- VIDEO_DURATION
- EMPLOYEE_STATUS
- GLOBAL_SUMMARY
- LIST_BY_STATUS

---

##  System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Chat UI    │  │  Auth Prompt │  │  State Management│   │
│  │  Components │  │              │  │  (Zustand)       │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  API Layer  │  │  Auth Service│  │  Training Service│   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  AI Agent Layer                       │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐  │  │
│  │  │ Guardrails  │ │Intent Parser │ │Training Agent│  │  │
│  │  └─────────────┘ └──────────────┘ └──────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              LLM Integration                          │  │
│  │  (OpenAI GPT-4 / Anthropic Claude / Local)          │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer (SQLite)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SQLAlchemy ORM  →  employees.db                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

1. **User Input** → Frontend React component
2. **Authentication Check** → Zustand auth store
3. **API Call** → Axios to FastAPI backend
4. **Guardrails Validation** → Multi-layer security checks
5. **Intent Parsing** → Natural language understanding
6. **Database Query** → Read-only SQLAlchemy operations
7. **LLM Generation** → Natural language response
8. **Response Sanitization** → Remove harmful content
9. **Display** → Formatted message in chat UI

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **ORM**: SQLAlchemy 2.0.25
- **Database**: SQLite (easily swappable to PostgreSQL/MySQL)
- **AI**: OpenAI GPT-4 / Anthropic Claude
- **NLP**: LangChain 0.1.4
- **Testing**: Pytest 7.4.4
- **Server**: Uvicorn (ASGI)

### Frontend
- **Framework**: React 18.2
- **Language**: TypeScript 5.3 (strict mode)
- **Build Tool**: Vite 5.0
- **State Management**: Zustand 4.5
- **HTTP Client**: Axios 1.6
- **Styling**: Tailwind CSS 3.4
- **Icons**: Lucide React
- **Markdown**: React Markdown

### DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (frontend)
- **Python Server**: Uvicorn (backend)
- **CI/CD Ready**: GitHub Actions compatible

---

##  Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for containerized setup)
- Git

### Local Development Setup

#### 1. Clone Repository

```bash
git clone <repository-url>
cd Automatiq_ai
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys

# Run backend
python run.py
```

Backend will be available at `http://localhost:8000`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

---

##  Running with Docker

### Quick Start (Recommended)

```bash
# 1. Create .env file
cp .env.example .env

# 2. Edit .env and add your LLM API key
nano .env  # or use any text editor

# 3. Start all services
docker-compose up --build

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend:  http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### 🎮 First Time Usage

After the services start, navigate to `http://localhost:3000`:

1. **Login with any employee from the database**:
   - Use any Employee ID and matching name from `employees.db`
   - Example: `873239713` + `Charlie Levi`
   
2. **CISO Access** (Special Privileges):
   - Employee ID: `123456789`
   - Name: Any name from the employee with ID 123456789
   - CISO can query ALL employees, not just their own data

3. **Start Asking Questions**:
   - "What is my training status?"
   - "Show me all employees who finished training" (CISO only)
   - "How many videos did Charlie Levi finish?" (CISO only)
   - "List employees who completed 2 or more videos" (CISO only)

### Individual Services

```bash
# Build backend
docker build -f Dockerfile.backend -t training-assistant-backend .

# Build frontend
docker build -f Dockerfile.frontend -t training-assistant-frontend .

# Run backend
docker run -p 8000:8000 --env-file .env training-assistant-backend

# Run frontend
docker run -p 3000:80 training-assistant-frontend
```

### Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# View running containers
docker-compose ps

# Execute commands in container
docker-compose exec backend python -m pytest
```

---

##  Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=sqlite:///./employees.db

# LLM Configuration
OPENAI_API_KEY=sk-...              # Your OpenAI API key
OPENAI_MODEL=gpt-4-turbo-preview   # Model to use
ANTHROPIC_API_KEY=sk-ant-...       # Your Anthropic API key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
LLM_PROVIDER=openai                # openai, anthropic, or local

# Application
APP_NAME=CyberSecurity Training Assistant
DEBUG=False
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Session
SESSION_TIMEOUT_MINUTES=30
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

---

##  API Documentation

### Endpoints

#### POST /api/session/create
Create a new session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": "Session created successfully"
}
```

#### POST /api/authenticate
Authenticate user with credentials.

**Request:**
```json
{
  "session_id": "uuid-string",
  "employee_id": 123,
  "employee_name": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "session_id": "uuid-string",
  "is_authenticated": true,
  "is_ciso": false,
  "missing_fields": []
}
```

#### POST /api/chat
Send a natural language query.

**Request:**
```json
{
  "session_id": "uuid-string",
  "query": "What is my training status?"
}
```

**Response:**
```json
{
  "success": true,
  "response": "You have completed 2 out of 5 videos...",
  "intent": "employee_status",
  "requires_auth": false,
  "context_data": {...}
}
```

#### POST /api/status/employee
Get detailed employee status.

**Request:**
```json
{
  "session_id": "uuid-string",
  "employee_id": 123  // Optional, CISO only
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 123,
    "employee_name": "John Doe",
    "status": "IN_PROGRESS",
    "completion_percentage": 40.0,
    "completed_videos": [1, 2],
    "missing_videos": [3, 4, 5],
    "video_details": [...]
  }
}
```

#### POST /api/status/all
Get global statistics (CISO only).

**Request:**
```json
{
  "session_id": "uuid-string",
  "status_filter": "FINISHED"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_employees": 100,
    "finished_employees_count": 75,
    "max_time_minutes": 120.5,
    "min_time_minutes": 45.2,
    "average_time_minutes": 82.3,
    "fastest_employee": {...},
    "slowest_employee": {...}
  }
}
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

##  Security & Guardrails

### Multi-Layer Protection

#### 1. Topic Validation
```python
# Only training-related keywords allowed
ALLOWED_TOPICS = [
    "training", "video", "completed", "status",
    "cybersecurity", "phishing", "password", ...
]
```

#### 2. SQL Injection Prevention
```python
# Detects patterns like:
# - '; DROP TABLE
# - UNION SELECT
# - -- comments
SQL_INJECTION_PATTERNS = [
    r"(\b(union|select|from|where)\b.*\b(select|from|where)\b)",
    r"(;|\-\-|\/\*|\*\/)",
    ...
]
```

#### 3. Forbidden Operations
```python
FORBIDDEN_KEYWORDS = [
    "update", "delete", "insert", "drop",
    "alter", "truncate", "exec", "system", ...
]
```

#### 4. Prompt Injection Detection
```python
# Blocks attempts to manipulate the AI
- "ignore previous instructions"
- "ignore prompt"
- "system prompt override"
```

#### 5. Response Sanitization
Removes potentially harmful content from AI responses before delivery to user.

### Authentication Security

- **No Password Storage**: Uses ID + Name verification against database
- **Session Timeout**: Automatic expiration after 30 minutes
- **CISO Protection**: Special credentials required for admin queries
- **Read-Only**: No write operations allowed on employee data

---

##  Example Scenarios

### Employee Use Cases

#### Scenario 1: Check Training Status
```
User: "What is my training status?"

AI: "You're currently IN_PROGRESS with your cybersecurity training. 
     You've completed 2 out of 5 videos (40% complete).
     
     Completed:
     ✓ Video 1: Introduction to Cybersecurity (15.5 minutes)
     ✓ Video 2: Password Security (20.0 minutes)
     
     Remaining:
     ✗ Video 3: Phishing Awareness
     ✗ Video 4: Data Protection
     ✗ Video 5: Incident Response
     
     Total time so far: 35.5 minutes"
```

#### Scenario 2: Check Specific Video
```
User: "How long did video 2 take me?"

AI: "You spent 20.0 minutes on Video 2: Password Security. 
     This video is marked as completed."
```

#### Scenario 3: Off-Topic Query (Blocked)
```
User: "What's the weather today?"

AI: "I can only answer questions about cybersecurity training.
     Please ask about:
     - Training completion status
     - Video progress and duration
     - Employee training statistics"
```

### CISO Use Cases

#### Scenario 4: Global Statistics
```
CISO: "Give me global training statistics"

AI: "Company-wide Training Statistics:
     
     Total Employees: 150
     - Finished: 90 (60%)
     - In Progress: 45 (30%)
     - Not Started: 15 (10%)
     
     Completion Times:
     - Average: 82.3 minutes
     - Fastest: 45.2 minutes (Alice Johnson)
     - Slowest: 120.5 minutes (Bob Smith)"
```

#### Scenario 5: Filter by Status
```
CISO: "Show me all employees who haven't started training"

AI: "Found 15 employees with status NOT_STARTED:
     
     1. John Doe (IT Department)
     2. Jane Smith (HR Department)
     3. Mike Johnson (Sales Department)
     ..."
```

---

##  Project Structure

```
Automatiq_ai/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── guardrails.py         # Security guardrails
│   │   │   ├── intent_parser.py      # NLP intent classification
│   │   │   └── training_agent.py     # Main AI agent
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py             # FastAPI endpoints
│   │   │   └── schemas.py            # Pydantic models
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py             # Configuration
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # SQLAlchemy base
│   │   │   └── session.py            # Database session
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── employee.py           # Employee ORM model
│   │   │   └── session.py            # Session model
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py       # Authentication logic
│   │   │   └── training_service.py   # Training queries
│   │   └── main.py                   # FastAPI app
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py               # Pytest fixtures
│   │   ├── test_api.py               # API tests
│   │   ├── test_guardrails.py        # Security tests
│   │   └── test_intent_parser.py     # NLP tests
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AuthPrompt.tsx        # Authentication UI
│   │   │   ├── ChatInput.tsx         # Message input
│   │   │   ├── ChatMessage.tsx       # Message display
│   │   │   ├── ErrorBoundary.tsx     # Error handling
│   │   │   └── LoadingSpinner.tsx    # Loading states
│   │   ├── pages/
│   │   │   └── ChatPage.tsx          # Main chat page
│   │   ├── services/
│   │   │   └── api.ts                # API client
│   │   ├── store/
│   │   │   ├── authStore.ts          # Auth state
│   │   │   └── chatStore.ts          # Chat state
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript types
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── .eslintrc.cjs
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── nginx.conf
├── .env.example
├── .gitignore
├── .dockerignore
├── README.md
├── documentation.pdf
└── employees.db
```

---

### Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_guardrails.py

# Run with verbose output
pytest -v
```

### Test Coverage

- ✅ API endpoint tests
- ✅ Guardrails security tests
- ✅ Intent parser NLP tests
- ✅ Authentication flow tests
- ✅ Database query tests

### Manual Testing

1. **Authentication Flow**:
   - Create session
   - Partial authentication (ID only)
   - Complete authentication
   - CISO login

2. **Employee Queries**:
   - Training status
   - Video completion
   - Time spent queries

3. **CISO Queries**:
   - Global statistics
   - Employee filtering
   - Performance metrics

4. **Security Tests**:
   - SQL injection attempts
   - Off-topic queries
   - Forbidden operations
   - Prompt injection

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend won't start

**Error**: `Module not found`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Error**: `Database file not found`
```bash
# Solution: Ensure employees.db is in the correct location
cp /path/to/employees.db ./backend/
```

#### 2. Frontend build fails

**Error**: `Cannot find module '@/...`'
```bash
# Solution: Check tsconfig.json paths and restart
npm run dev
```

#### 3. Docker issues

**Error**: `Port already in use`
```bash
# Solution: Change ports in docker-compose.yml or stop conflicting services
docker-compose down
```

**Error**: `Cannot connect to database`
```bash
# Solution: Ensure database volume is mounted
docker-compose down -v
docker-compose up --build
```

#### 4. LLM API errors

**Error**: `Invalid API key`
```bash
# Solution: Check .env file has correct API key
# For OpenAI: OPENAI_API_KEY=sk-...
# For Anthropic: ANTHROPIC_API_KEY=sk-ant-...
```

**Error**: `Rate limit exceeded`
```bash
# Solution: Wait or switch LLM provider in .env
LLM_PROVIDER=anthropic
```

### Debug Mode

```bash
# Enable debug mode in .env
DEBUG=True
LOG_LEVEL=DEBUG

# View detailed logs
docker-compose logs -f backend
```

---
