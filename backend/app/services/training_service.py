"""
Training Service
~~~~~~~~~~~~~~~~

Business logic for querying and analyzing cybersecurity training data.
Provides read-only operations with comprehensive error handling.
"""

from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.employee import Employee


class TrainingService:
    """
    Service class for training-related operations.
    
    Implements all business logic for querying employee training data.
    All operations are read-only to maintain data integrity.
    """
    
    VIDEO_NAMES = {
        1: "First Cybersecurity Video",
        2: "Second Cybersecurity Video",
        3: "Third Cybersecurity Video",
        4: "Fourth Cybersecurity Video"
    }
    
    def __init__(self, db: Session):
        """
        Initialize training service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """
        Get employee by ID.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            Employee object if found, None otherwise
        """
        # Convert to string with padding
        employee_id_str = str(employee_id).zfill(9)
        return self.db.query(Employee).filter(Employee.EMPLOYEE_ID == employee_id_str).first()
    
    def get_employee_by_name(self, name: str) -> Optional[Employee]:
        """
        Get employee by exact name match (first name or full name).
        
        Args:
            name: Employee name
            
        Returns:
            Employee object if found, None otherwise
        """
        # Try full name match first
        employees = self.db.query(Employee).all()
        for emp in employees:
            if emp.full_name.lower() == name.lower():
                return emp
            if emp.EMPLOYEE_NAME.lower() == name.lower():
                return emp
        return None
    
    def verify_employee_credentials(
        self,
        employee_id: int,
        name: str
    ) -> Tuple[bool, Optional[Employee]]:
        """
        Verify employee credentials (ID + name match).
        
        Args:
            employee_id: Employee ID
            name: Employee name
            
        Returns:
            Tuple of (is_valid, employee_object)
        """
        # Get employee by ID
        employee = self.get_employee_by_id(employee_id)
        
        if not employee:
            return (False, None)
        
        # Check if name matches (first name or full name)
        name_lower = name.lower()
        if (employee.EMPLOYEE_NAME.lower() == name_lower or 
            employee.full_name.lower() == name_lower):
            return (True, employee)
        
        return (False, None)
    
    def get_employee_status(self, employee_id: int) -> Dict:
        """
        Get comprehensive status for a single employee.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            Dictionary with employee status information
        """
        employee = self.get_employee_by_id(employee_id)
        
        if not employee:
            return {"error": "Employee not found"}
        
        completed_videos = employee.get_completed_videos()
        missing_videos = employee.get_missing_videos()
        
        # Build video details
        video_details = []
        for i in range(1, 5):  # Only 4 videos in this database
            video_details.append({
                "video_number": i,
                "video_name": self.VIDEO_NAMES[i],
                "completed": employee.get_video_completed(i),
                "duration_minutes": employee.get_video_duration(i)
            })
        
        return {
            "employee_id": employee.EMPLOYEE_ID,
            "employee_name": employee.full_name,
            "email": employee.email,
            "department": employee.EMPLOYEE_DIVISION,
            "status": employee.get_training_status(),
            "completion_percentage": employee.completion_percentage,
            "total_time_minutes": employee.total_time,
            "completed_videos": completed_videos,
            "completed_videos_count": len(completed_videos),
            "missing_videos": missing_videos,
            "missing_videos_count": len(missing_videos),
            "video_details": video_details,
            "started_at": employee.started_at.isoformat() if employee.started_at else None,
            "completed_at": employee.completed_at.isoformat() if employee.completed_at else None,
        }
    
    def get_employees_by_status(self, status: str) -> List[Dict]:
        """
        Get all employees matching a specific status.
        
        Args:
            status: One of NOT_STARTED, IN_PROGRESS, or FINISHED
            
        Returns:
            List of employee status dictionaries
        """
        # Query all employees
        employees = self.db.query(Employee).all()
        
        # Filter by status
        filtered_employees = []
        for employee in employees:
            if employee.get_training_status() == status:
                filtered_employees.append({
                    "employee_id": employee.id,
                    "employee_name": employee.name,
                    "email": employee.email,
                    "department": employee.department,
                    "status": status,
                    "completion_percentage": employee.completion_percentage,
                    "total_time_minutes": employee.total_time,
                })
        
        return filtered_employees
    
    def get_global_summary(self) -> Dict:
        """
        Get global training summary across all employees.
        
        Returns:
            Dictionary with aggregated statistics
        """
        # Get ALL employees (can't filter by hybrid properties in SQL)
        all_employees = self.db.query(Employee).all()
        
        if not all_employees:
            return {
                "total_employees": 0,
                "finished_employees_count": 0,
                "not_started_count": 0,
                "in_progress_count": 0,
                "max_time_minutes": 0,
                "min_time_minutes": 0,
                "average_time_minutes": 0,
                "fastest_employee": None,
                "slowest_employee": None,
            }
        
        # Filter by status in Python (hybrid properties can't be used in SQL WHERE)
        finished_employees = [e for e in all_employees if e.get_training_status() == "FINISHED"]
        not_started = [e for e in all_employees if e.get_training_status() == "NOT_STARTED"]
        in_progress = [e for e in all_employees if e.get_training_status() == "IN_PROGRESS"]
        
        if not finished_employees:
            return {
                "total_employees": len(all_employees),
                "finished_employees_count": 0,
                "not_started_count": len(not_started),
                "in_progress_count": len(in_progress),
                "max_time_minutes": 0,
                "min_time_minutes": 0,
                "average_time_minutes": 0,
                "fastest_employee": None,
                "slowest_employee": None,
            }
        
        # Calculate statistics from finished employees
        times = [e.total_time for e in finished_employees]
        max_time = max(times)
        min_time = min(times)
        avg_time = sum(times) / len(times)
        
        # Find fastest and slowest
        fastest = min(finished_employees, key=lambda e: e.total_time)
        slowest = max(finished_employees, key=lambda e: e.total_time)
        
        return {
            "total_employees": len(all_employees),
            "finished_employees_count": len(finished_employees),
            "not_started_count": len(not_started),
            "in_progress_count": len(in_progress),
            "max_time_minutes": max_time,
            "min_time_minutes": min_time,
            "average_time_minutes": round(avg_time, 2),
            "fastest_employee": {
                "id": fastest.id,
                "name": fastest.name,
                "time_minutes": fastest.total_time
            },
            "slowest_employee": {
                "id": slowest.id,
                "name": slowest.name,
                "time_minutes": slowest.total_time
            },
        }
    
    def get_video_name(self, video_number: int) -> str:
        """
        Get video name by number.
        
        Args:
            video_number: Video number (1-5)
            
        Returns:
            Video name or error message
        """
        return self.VIDEO_NAMES.get(video_number, f"Unknown video {video_number}")
    
    def search_employees(self, query: str) -> List[Employee]:
        """
        Search employees by name.
        
        Args:
            query: Search query
            
        Returns:
            List of matching employees
        """
        return self.db.query(Employee).filter(
            Employee.name.ilike(f"%{query}%")
        ).all()
    
    def get_employees_by_video_count(self, count: int, operator: str = ">=") -> List[Dict]:
        """
        Get employees who have completed a certain number of videos.
        
        Args:
            count: Number of videos
            operator: Comparison operator (>=, <=, ==, >, <)
            
        Returns:
            List of employee dictionaries
        """
        all_employees = self.db.query(Employee).all()
        filtered = []
        
        for emp in all_employees:
            completed_count = len(emp.get_completed_videos())
            
            if operator == ">=" and completed_count >= count:
                matches = True
            elif operator == "<=" and completed_count <= count:
                matches = True
            elif operator == "==" and completed_count == count:
                matches = True
            elif operator == ">" and completed_count > count:
                matches = True
            elif operator == "<" and completed_count < count:
                matches = True
            else:
                matches = False
            
            if matches:
                filtered.append({
                    "employee_id": emp.EMPLOYEE_ID,
                    "employee_name": emp.full_name,
                    "email": emp.email,
                    "department": emp.EMPLOYEE_DIVISION,
                    "completed_videos_count": completed_count,
                    "completion_percentage": emp.completion_percentage,
                    "status": emp.get_training_status(),
                })
        
        return filtered

