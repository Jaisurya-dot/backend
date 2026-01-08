from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.db_config import get_db
from models.question import Question, Option
from models.exam_room import ExamRoom
from models.user import User
from schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionOut,
    OptionCreate, OptionUpdate, OptionResponse
)
from core.auth import get_current_active_user, require_admin

router = APIRouter(prefix="/questions", tags=["questions"])

@router.post("/exam-room/{exam_room_id}", response_model=QuestionResponse)
def create_question_nested(
    exam_room_id: int,
    question: QuestionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Check if exam room exists
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == exam_room_id).first()
    if not exam_room:
        raise HTTPException(status_code=404, detail="Exam room not found")
    
    # Create question
    db_question = Question(
        exam_room_id=exam_room_id,
        question_text=question.question_text,
        marks=question.marks,
        order_index=question.order_index
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    # Create options
    for opt in question.options:
        db_option = Option(
            question_id=db_question.id,
            option_text=opt.option_text,
            is_correct=opt.is_correct
        )
        db.add(db_option)
    
    db.commit()
    db.refresh(db_question)
    return db_question

@router.get("/exam-room/{exam_room_id}", response_model=List[QuestionOut])
def get_questions_by_exam_room(
    exam_room_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if exam room exists and user has access
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == exam_room_id).first()
    if not exam_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam room not found"
        )
    
    # Check access permissions
    if current_user.role != "ADMIN" and exam_room.created_by != current_user.id:
        if not exam_room.is_published:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    questions = db.query(Question).filter(
        Question.exam_room_id == exam_room_id
    ).order_by(Question.order_index).all()
    
    return questions

@router.get("/{question_id}", response_model=QuestionResponse)
def get_question_by_id(
    question_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if user has permission
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == question.exam_room_id).first()
    if exam_room.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return question

@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    question_update: QuestionUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if user has permission
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == question.exam_room_id).first()
    if exam_room.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update question
    update_data = question_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)
    
    db.commit()
    db.refresh(question)
    return question

@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if user has permission
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == question.exam_room_id).first()
    if exam_room.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}

# Option management endpoints
@router.post("/{question_id}/options", response_model=OptionResponse)
def create_option(
    question_id: int,
    option: OptionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if user has permission
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == question.exam_room_id).first()
    if exam_room.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if question already has max options
    current_options = db.query(Option).filter(Option.question_id == question_id).count()
    if current_options >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 options allowed per question"
        )
    
    db_option = Option(
        question_id=question_id,
        option_text=option.option_text,
        is_correct=option.is_correct
    )
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    return db_option

@router.put("/options/{option_id}", response_model=OptionResponse)
def update_option(
    option_id: int,
    option_update: OptionUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    option = db.query(Option).filter(Option.id == option_id).first()
    if not option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found"
        )
    
    # Check if user has permission
    question = db.query(Question).filter(Question.id == option.question_id).first()
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == question.exam_room_id).first()
    if exam_room.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    update_data = option_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(option, field, value)
    
    db.commit()
    db.refresh(option)
    return option

@router.delete("/options/{option_id}")
def delete_option(
    option_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    option = db.query(Option).filter(Option.id == option_id).first()
    if not option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found"
        )
    
    # Check if user has permission
    question = db.query(Question).filter(Question.id == option.question_id).first()
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == question.exam_room_id).first()
    if exam_room.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if question has minimum options
    current_options = db.query(Option).filter(Option.question_id == option.question_id).count()
    if current_options <= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum 2 options required per question"
        )
    
    db.delete(option)
    db.commit()
    return {"message": "Option deleted successfully"}
