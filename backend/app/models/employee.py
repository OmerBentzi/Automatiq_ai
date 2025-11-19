"""
Real Employee Model - Matches Actual Database Schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from app.db.base import Base


class Employee(Base):
    """
    Employee ORM model for the REAL database schema.
    """
    
    __tablename__ = "employees"
    __table_args__ = {"extend_existing": True}
    
    # Primary Key
    EMPLOYEE_ID = Column(String(9), primary_key=True)
    
    # Employee Information
    EMPLOYEE_NAME = Column(String(255), nullable=False)
    EMPLOYEE_LAST_NAME = Column(String(255), nullable=False)
    EMPLOYEE_DIVISION = Column(String(100), nullable=False)
    
    # Video 1
    START_FIRST_VIDEO_DATE = Column(DateTime)
    FINISH_FIRST_VIDEO_DATE = Column(DateTime)
    
    # Video 2
    START_SECOND_VIDEO_DATE = Column(DateTime)
    FINISH_SECOND_VIDEO_DATE = Column(DateTime)
    
    # Video 3
    START_THIRD_VIDEO_DATE = Column(DateTime)
    FINISH_THIRD_VIDEO_DATE = Column(DateTime)
    
    # Video 4
    START_FOURTH_VIDEO_DATE = Column(DateTime)
    FINISH_FOURTH_VIDEO_DATE = Column(DateTime)
    
    def __repr__(self) -> str:
        return f"<Employee(id={self.EMPLOYEE_ID}, name='{self.full_name}')>"
    
    @hybrid_property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.EMPLOYEE_NAME} {self.EMPLOYEE_LAST_NAME}"
    
    @hybrid_property
    def id(self) -> str:
        """Alias for EMPLOYEE_ID"""
        return self.EMPLOYEE_ID
    
    @hybrid_property
    def name(self) -> str:
        """Alias for full name"""
        return self.full_name
    
    @hybrid_property
    def department(self) -> str:
        """Alias for division"""
        return self.EMPLOYEE_DIVISION
    
    @hybrid_property
    def email(self) -> str:
        """Generate email from name"""
        return f"{self.EMPLOYEE_NAME.lower()}.{self.EMPLOYEE_LAST_NAME.lower()}@company.com"
    
    def get_video_completed(self, video_num: int) -> bool:
        """Check if a video is completed"""
        video_map = {
            1: self.FINISH_FIRST_VIDEO_DATE,
            2: self.FINISH_SECOND_VIDEO_DATE,
            3: self.FINISH_THIRD_VIDEO_DATE,
            4: self.FINISH_FOURTH_VIDEO_DATE,
        }
        finish_date = video_map.get(video_num)
        return finish_date is not None
    
    def get_video_duration(self, video_num: int) -> float:
        """Calculate video duration in minutes"""
        video_map = {
            1: (self.START_FIRST_VIDEO_DATE, self.FINISH_FIRST_VIDEO_DATE),
            2: (self.START_SECOND_VIDEO_DATE, self.FINISH_SECOND_VIDEO_DATE),
            3: (self.START_THIRD_VIDEO_DATE, self.FINISH_THIRD_VIDEO_DATE),
            4: (self.START_FOURTH_VIDEO_DATE, self.FINISH_FOURTH_VIDEO_DATE),
        }
        start, finish = video_map.get(video_num, (None, None))
        if start and finish:
            delta = finish - start
            return round(delta.total_seconds() / 60, 2)
        return 0.0
    
    def get_completed_videos(self) -> list[int]:
        """Get list of completed video numbers"""
        return [i for i in range(1, 5) if self.get_video_completed(i)]
    
    def get_missing_videos(self) -> list[int]:
        """Get list of missing video numbers"""
        return [i for i in range(1, 5) if not self.get_video_completed(i)]
    
    def get_training_status(self) -> str:
        """Get training status"""
        completed = self.get_completed_videos()
        if len(completed) == 0:
            return "NOT_STARTED"
        elif len(completed) == 4:
            return "FINISHED"
        else:
            return "IN_PROGRESS"
    
    @hybrid_property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        completed = len(self.get_completed_videos())
        return round((completed / 4) * 100, 2)
    
    @hybrid_property
    def total_time(self) -> float:
        """Calculate total time spent"""
        return sum(self.get_video_duration(i) for i in range(1, 5))
    
    @hybrid_property
    def started_at(self) -> datetime:
        """Get earliest start date"""
        dates = [
            self.START_FIRST_VIDEO_DATE,
            self.START_SECOND_VIDEO_DATE,
            self.START_THIRD_VIDEO_DATE,
            self.START_FOURTH_VIDEO_DATE,
        ]
        valid_dates = [d for d in dates if d]
        return min(valid_dates) if valid_dates else None
    
    @hybrid_property
    def completed_at(self) -> datetime:
        """Get completion date if all videos finished"""
        if self.get_training_status() == "FINISHED":
            dates = [
                self.FINISH_FIRST_VIDEO_DATE,
                self.FINISH_SECOND_VIDEO_DATE,
                self.FINISH_THIRD_VIDEO_DATE,
                self.FINISH_FOURTH_VIDEO_DATE,
            ]
            valid_dates = [d for d in dates if d]
            return max(valid_dates) if valid_dates else None
        return None

