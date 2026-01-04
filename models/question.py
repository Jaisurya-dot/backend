from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import   relationship
from db.db_config import  Base

 

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_room_id = Column(Integer, ForeignKey("exam_rooms.id"), nullable=False, index=True)
    question_text = Column(String(1000), nullable=False)
    marks = Column(Integer, default=1)
    order_index = Column(Integer, default=0, index=True)
    
    # Relationships
    exam_room = relationship("ExamRoom", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    
    

class Option(Base):
    
    __tablename__ = "options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    option_text = Column(String(500), nullable=False)
    is_correct = Column(Boolean, default=False)
    
    # Relationships
    question = relationship("Question", back_populates="options")
    
    