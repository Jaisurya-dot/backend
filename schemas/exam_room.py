from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ExamRoomBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: datetime
    end_time: datetime
    duration_minutes: int = Field(..., ge=1, le=300)  # 1-300 minutes
    total_marks: int = Field(..., ge=0)
    is_published: bool = False

class ExamRoomCreate(ExamRoomBase):
    pass

class ExamRoomUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=300)
    total_marks: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None

class ExamRoomResponse(ExamRoomBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ExamRoomOut(ExamRoomBase):
    id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExamRoomWithQuestions(ExamRoomResponse):
    questions: List['QuestionResponse'] = []

# Import at the end to avoid circular imports
from schemas.question import QuestionResponse
ExamRoomWithQuestions.model_rebuild()
