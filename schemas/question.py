from pydantic import BaseModel, Field
from typing import List, Optional

class OptionBase(BaseModel):
    option_text: str = Field(..., max_length=500)

class OptionCreate(OptionBase):
    is_correct: bool = False

class OptionUpdate(BaseModel):
    option_text: Optional[str] = Field(None, max_length=500)
    is_correct: Optional[bool] = None

class OptionResponse(OptionBase):
    id: int
    is_correct: bool
    
    class Config:
        from_attributes = True

class OptionOut(OptionBase):
    id: int
    
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    question_text: str = Field(..., max_length=1000)
    marks: int = Field(default=1, ge=1, le=10)
    order_index: int = Field(default=0, ge=0)

class QuestionCreate(QuestionBase):
    options: List[OptionCreate] = Field(..., min_items=2, max_items=6)

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, max_length=1000)
    marks: Optional[int] = Field(None, ge=1, le=10)
    order_index: Optional[int] = Field(None, ge=0)

class QuestionResponse(QuestionBase):
    id: int
    exam_room_id: int
    options: List[OptionResponse]
    
    class Config:
        from_attributes = True

class QuestionOut(QuestionBase):
    id: int
    options: List[OptionOut]
    
    class Config:
        from_attributes = True
