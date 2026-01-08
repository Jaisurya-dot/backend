from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import  relationship
from db.db_config import  Base
from datetime import datetime
import enum

 

class SubmissionStatus(str, enum.Enum):
    """Submission status enum"""
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    AUTO_SUBMITTED = "AUTO_SUBMITTED"

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_room_id = Column(Integer, ForeignKey("exam_rooms.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    submitted_at = Column(DateTime, nullable=True, index=True)
    status = Column(Enum(SubmissionStatus, name="submissionstatus"), default=SubmissionStatus.IN_PROGRESS, index=True)
    total_score = Column(Integer, default=0)
    time_taken_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exam_room = relationship("ExamRoom", back_populates="submissions")
    student = relationship("User")
    answers = relationship("Answer", back_populates="submission", cascade="all, delete-orphan")
    
    


class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    selected_option_id = Column(Integer, ForeignKey("options.id"), nullable=True)
    is_correct = Column(Boolean, default=False)
    
    # Relationships
    submission = relationship("Submission", back_populates="answers")
    
    
