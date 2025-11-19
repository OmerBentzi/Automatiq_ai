"""
Training Agent Module
~~~~~~~~~~~~~~~~~~~~~

Main AI agent for handling cybersecurity training queries.
Integrates LLM with guardrails, intent parsing, and database queries.
"""

from typing import Dict, Optional
from sqlalchemy.orm import Session
import openai
from anthropic import Anthropic

from app.core.config import settings
from app.services.training_service import TrainingService
from app.services.auth_service import AuthService
from app.agents.guardrails import Guardrails
from app.agents.intent_parser import IntentParser, Intent


class TrainingAgent:
    """
    AI-powered training assistant agent.
    
    This agent:
    1. Validates queries through guardrails
    2. Parses natural language intent
    3. Retrieves relevant data from database
    4. Generates natural language responses using LLM
    5. Enforces read-only operations
    """
    
    # System prompt for the LLM
    SYSTEM_PROMPT = """You are a helpful AI assistant for a cybersecurity training platform.

Your role is to help employees and the CISO understand training progress and status.

STRICT RULES:
1. ONLY answer questions about cybersecurity training
2. NEVER discuss topics unrelated to training
3. NEVER perform or suggest data modifications
4. NEVER execute any commands or operations
5. Be professional, clear, and concise
6. If asked about other topics, politely redirect to training-related questions

AVAILABLE INFORMATION:
- Employee training completion status
- Video completion details (5 videos total)
- Time spent on each video
- Overall progress percentage
- Global statistics (for CISO)

RESPONSE STYLE:
- Be friendly and professional
- Use clear, simple language
- Provide specific numbers when available
- Organize information clearly
- Always focus on training data

When given data, format it in a clear, readable way for the user."""
    
    def __init__(self, db: Session):
        """
        Initialize training agent.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.training_service = TrainingService(db)
        self.auth_service = AuthService(db)
        
        # Initialize LLM based on provider
        self._init_llm()
    
    def _init_llm(self) -> None:
        """Initialize LLM client based on configuration"""
        if settings.llm_provider == "openai":
            openai.api_key = settings.openai_api_key
        elif settings.llm_provider == "anthropic":
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
    
    def _call_llm(self, user_message: str, context_data: Optional[Dict] = None) -> str:
        """
        Call LLM with user message and optional context data.
        
        Args:
            user_message: User's question
            context_data: Optional data to provide as context
            
        Returns:
            LLM response
        """
        # Build the user prompt with context
        if context_data:
            context_str = f"\n\nRELEVANT DATA:\n{self._format_context_data(context_data)}\n\n"
            full_prompt = f"{context_str}USER QUESTION: {user_message}\n\nProvide a clear, natural response based on the data above."
        else:
            full_prompt = user_message
        
        try:
            if settings.llm_provider == "openai" and settings.openai_api_key:
                response = openai.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            
            elif settings.llm_provider == "anthropic" and settings.anthropic_api_key:
                message = self.anthropic_client.messages.create(
                    model=settings.anthropic_model,
                    max_tokens=1000,
                    system=self.SYSTEM_PROMPT,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ]
                )
                return message.content[0].text
            
            else:
                # Fallback for local/mock or missing API key
                return self._mock_response(user_message, context_data)
        
        except Exception as e:
            # Log error and fallback to rule-based response on LLM error
            print(f"LLM Error: {str(e)}")
            return self._mock_response(user_message, context_data)
    
    def _mock_response(self, user_message: str, context_data: Optional[Dict] = None) -> str:
        """
        Generate a rule-based response when LLM is unavailable.
        
        Args:
            user_message: User's question
            context_data: Optional context data
            
        Returns:
            Formatted response
        """
        if not context_data:
            return "I can help you with cybersecurity training questions. What would you like to know?"
        
        # Format context data into readable response with better formatting
        response_parts = []
        
        if "employee_name" in context_data:
            response_parts.append(f"**Training Status for {context_data['employee_name']}**\n")
        
        if "status" in context_data:
            response_parts.append(f"Status: **{context_data['status']}**")
        
        if "completion_percentage" in context_data:
            response_parts.append(f"Completion: **{context_data['completion_percentage']}%**")
        
        if "completed_videos" in context_data:
            completed = context_data['completed_videos']
            if completed:
                response_parts.append(f"\n**Completed Videos:** {len(completed)} out of 5")
                response_parts.append(f"Video numbers: {completed}")
        
        if "missing_videos" in context_data:
            missing = context_data['missing_videos']
            if missing:
                response_parts.append(f"\n**Missing Videos:** {len(missing)}")
                response_parts.append(f"Video numbers: {missing}")
        
        if "total_time_minutes" in context_data:
            time_min = context_data['total_time_minutes']
            response_parts.append(f"\n**Total Time Spent:** {time_min} minutes")
        
        if "video_details" in context_data:
            response_parts.append("\n**Detailed Video Status:**")
            for video in context_data['video_details']:
                status_icon = "✅" if video.get('completed') else "❌"
                response_parts.append(
                    f"{status_icon} Video {video['video_number']}: {video['video_name']} ({video['duration_minutes']} min)"
                )
        
        # Global summary formatting
        if "total_employees" in context_data:
            response_parts.append("\n**Company-wide Training Statistics:**\n")
            response_parts.append(f"📊 Total Employees: {context_data['total_employees']}")
            response_parts.append(f"✅ Finished: {context_data.get('finished_employees_count', 0)}")
            response_parts.append(f"🔄 In Progress: {context_data.get('in_progress_count', 0)}")
            response_parts.append(f"⏸️  Not Started: {context_data.get('not_started_count', 0)}")
            
            if context_data.get('average_time_minutes'):
                response_parts.append(f"\n⏱️  **Completion Times:**")
                response_parts.append(f"Average: {context_data['average_time_minutes']} minutes")
                response_parts.append(f"Minimum: {context_data['min_time_minutes']} minutes")
                response_parts.append(f"Maximum: {context_data['max_time_minutes']} minutes")
                
                if context_data.get('fastest_employee'):
                    fastest = context_data['fastest_employee']
                    response_parts.append(f"\n🚀 Fastest: {fastest['name']} ({fastest['time_minutes']} min)")
                
                if context_data.get('slowest_employee'):
                    slowest = context_data['slowest_employee']
                    response_parts.append(f"🐢 Slowest: {slowest['name']} ({slowest['time_minutes']} min)")
        
        if response_parts:
            return "\n".join(response_parts)
        else:
            return self._format_context_data(context_data)
    
    def _format_context_data(self, data: Dict) -> str:
        """
        Format context data into readable string.
        
        Args:
            data: Context data dictionary
            
        Returns:
            Formatted string
        """
        lines = []
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}: {', '.join(map(str, value))}")
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def process_query(
        self,
        query: str,
        session_id: str
    ) -> Dict:
        """
        Process a user query through the complete agent pipeline.
        
        Args:
            query: User's natural language question
            session_id: Session identifier
            
        Returns:
            Response dictionary with answer and metadata
        """
        # Step 1: Validate query through guardrails
        is_valid, error_message = Guardrails.validate_query(query)
        if not is_valid:
            return {
                "success": False,
                "response": error_message,
                "requires_auth": False
            }
        
        # Step 2: Check authentication
        if not self.auth_service.is_authenticated(session_id):
            return {
                "success": False,
                "response": "Please authenticate with your employee ID and name first.",
                "requires_auth": True
            }
        
        # Step 3: Parse intent
        parsed = IntentParser.parse(query)
        intent = parsed["intent"]
        
        # Step 4: Check if CISO query
        is_ciso = self.auth_service.is_ciso(session_id)
        is_ciso_query = IntentParser.is_ciso_query(query)
        
        if is_ciso_query and not is_ciso:
            return {
                "success": False,
                "response": "You don't have permission to access company-wide statistics. CISO access required.",
                "requires_auth": False
            }
        
        # Step 5: Get employee ID
        employee_id = self.auth_service.get_authenticated_employee_id(session_id)
        
        # Step 6: Retrieve relevant data based on intent
        context_data = self._get_context_data(intent, parsed, employee_id, is_ciso)
        
        # Step 7: Generate response using LLM
        llm_response = self._call_llm(query, context_data)
        
        # Step 8: Sanitize response
        safe_response = Guardrails.sanitize_response(llm_response)
        
        return {
            "success": True,
            "response": safe_response,
            "intent": intent.value,
            "context_data": context_data,
            "requires_auth": False
        }
    
    def _get_context_data(
        self,
        intent: Intent,
        parsed: Dict,
        employee_id: int,
        is_ciso: bool
    ) -> Dict:
        """
        Retrieve context data based on intent.
        
        Args:
            intent: Parsed intent
            parsed: Full parsed query data
            employee_id: Employee ID (logged-in user)
            is_ciso: Whether user is CISO
            
        Returns:
            Context data dictionary
        """
        # Check if CISO is asking about a specific employee
        target_employee_id = employee_id
        employee_name = parsed.get("employee_name")
        
        if is_ciso and employee_name:
            # CISO asking about another employee - look them up by name
            employee = self.training_service.get_employee_by_name(employee_name)
            if employee:
                target_employee_id = int(employee.EMPLOYEE_ID)
            else:
                return {"error": f"Employee '{employee_name}' not found in database"}
        
        if intent == Intent.EMPLOYEE_STATUS:
            return self.training_service.get_employee_status(target_employee_id)
        
        elif intent == Intent.CHECK_COMPLETION:
            status = self.training_service.get_employee_status(target_employee_id)
            return {
                "training_completed": status["status"] == "FINISHED",
                "completion_percentage": status["completion_percentage"],
                "completed_videos": status["completed_videos"],
                "missing_videos": status["missing_videos"]
            }
        
        elif intent == Intent.LIST_COMPLETED_VIDEOS:
            status = self.training_service.get_employee_status(target_employee_id)
            return {
                "completed_videos": status["completed_videos"],
                "video_details": [
                    v for v in status["video_details"] if v["completed"]
                ]
            }
        
        elif intent == Intent.LIST_MISSING_VIDEOS:
            status = self.training_service.get_employee_status(target_employee_id)
            return {
                "missing_videos": status["missing_videos"],
                "video_details": [
                    v for v in status["video_details"] if not v["completed"]
                ]
            }
        
        elif intent == Intent.VIDEO_DURATION:
            video_num = parsed["video_number"]
            status = self.training_service.get_employee_status(target_employee_id)
            if video_num:
                video_detail = next(
                    (v for v in status["video_details"] if v["video_number"] == video_num),
                    None
                )
                return {"video": video_detail} if video_detail else {}
            return {"all_videos": status["video_details"]}
        
        elif intent == Intent.GLOBAL_SUMMARY and is_ciso:
            return self.training_service.get_global_summary()
        
        elif intent == Intent.LIST_BY_STATUS and is_ciso:
            status_filter = parsed["status"]
            if status_filter:
                employees = self.training_service.get_employees_by_status(status_filter)
                return {
                    "status": status_filter,
                    "employees": employees,
                    "count": len(employees)
                }
            return {}
        
        elif intent == Intent.LIST_BY_VIDEO_COUNT and is_ciso:
            video_count_filter = parsed["video_count_filter"]
            if video_count_filter:
                count = video_count_filter["count"]
                operator = video_count_filter["operator"]
                employees = self.training_service.get_employees_by_video_count(count, operator)
                return {
                    "filter": f"{operator} {count} videos",
                    "employees": employees,
                    "count": len(employees)
                }
            return {}
        
        else:
            # General question - return full employee status
            return self.training_service.get_employee_status(target_employee_id)

