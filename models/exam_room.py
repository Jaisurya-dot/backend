from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import   relationship
from db.db_config import  Base
from datetime import datetime

 

class ExamRoom(Base):
    __tablename__ = "exam_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False )
    description = Column(String(1000))
    start_time = Column(DateTime, nullable=False )
    end_time = Column(DateTime, nullable=False )
    duration_minutes = Column(Integer, nullable=False)
    total_marks = Column(Integer, nullable=False, default=0)
    is_published = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    questions = relationship("Question", back_populates="exam_room", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="exam_room", cascade="all, delete-orphan")
