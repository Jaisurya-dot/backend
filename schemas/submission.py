from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnswerCreate(BaseModel):
    question_id: int
    selected_option_id: Optional[int] = None

class AnswerUpdate(BaseModel):
    selected_option_id: Optional[int] = None

class AnswerResponse(BaseModel):
    id: int
    question_id: int
    selected_option_id: Optional[int]
    is_correct: bool
    
    class Config:
        from_attributes = True

class AnswerResult(BaseModel):
    question_id: int
    selected_option_id: Optional[int]
    correct_option_id: Optional[int]
    is_correct: bool

class SubmissionBase(BaseModel):
    exam_room_id: int

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionResponse(SubmissionBase):
    id: int
    student_id: int
    started_at: datetime
    submitted_at: Optional[datetime]
    status: str
    total_score: int
    time_taken_seconds: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SubmissionStartResponse(BaseModel):
    submission_id: int
    exam_room_id: int
    exam_room_title: str
    duration_minutes: int
    questions: List[dict]

class SubmissionResult(BaseModel):
    submission_id: int
    total_score: int
    status: str
    answers: List[AnswerResult]

class SubmissionHistory(BaseModel):
    exam_id: int
    score: int
    status: str
    submitted_at: Optional[datetime]

class SubmissionHistoryResponse(BaseModel):
    id: int
    exam_room_id: int
    exam_room_title: str
    total_score: int
    status: str
    started_at: datetime
    submitted_at: Optional[datetime]
    time_taken_seconds: Optional[int]
    
    class Config:
        from_attributes = True
