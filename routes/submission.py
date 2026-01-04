from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from db.db_config import get_db
from models.submission import Submission, Answer, SubmissionStatus
from models.question import Question, Option
from models.exam_room import ExamRoom
from models.user import User
from schemas.submission import (
    SubmissionCreate, SubmissionResponse, SubmissionStartResponse,
    SubmissionResult, SubmissionHistoryResponse,
    AnswerCreate, AnswerUpdate, AnswerResponse, AnswerResult
)
from schemas.question import QuestionOut
from core.auth import get_current_active_user

router = APIRouter(prefix="/submissions", tags=["submissions"])

@router.post("/start", response_model=SubmissionStartResponse)
def start_submission(
    submission: SubmissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if exam room exists and is published
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == submission.exam_room_id).first()
    if not exam_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam room not found"
        )
    
    if not exam_room.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam room is not published"
        )
    
    # Check if exam is still active
    now = datetime.utcnow()
    if now < exam_room.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam has not started yet"
        )
    
    if now > exam_room.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam has ended"
        )
    
    # Check if user already has an active submission
    existing_submission = db.query(Submission).filter(
        Submission.exam_room_id == submission.exam_room_id,
        Submission.student_id == current_user.id,
        Submission.status == SubmissionStatus.IN_PROGRESS
    ).first()
    
    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active submission for this exam"
        )
    
    # Create new submission
    db_submission = Submission(
        exam_room_id=submission.exam_room_id,
        student_id=current_user.id
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    # Get questions for the exam
    questions = db.query(Question).filter(
        Question.exam_room_id == submission.exam_room_id
    ).order_by(Question.order_index).all()
    
    # Format questions for response (hide correct answers)
    formatted_questions = []
    for question in questions:
        options = []
        for option in question.options:
            options.append({
                "id": option.id,
                "option_text": option.option_text
            })
        
        formatted_questions.append({
            "id": question.id,
            "question_text": question.question_text,
            "marks": question.marks,
            "order_index": question.order_index,
            "options": options
        })
    
    return SubmissionStartResponse(
        submission_id=db_submission.id,
        exam_room_id=exam_room.id,
        duration_minutes=exam_room.duration_minutes,
        questions=formatted_questions
    )

@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Check if user owns this submission
    if submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return submission

@router.post("/{submission_id}/answers", response_model=AnswerResponse)
def save_answer(
    submission_id: int,
    answer: AnswerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Check if user owns this submission
    if submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if submission is still active
    if submission.status != SubmissionStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission is not active"
        )
    
    # Check if exam time has expired
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == submission.exam_room_id).first()
    time_elapsed = datetime.utcnow() - submission.started_at
    if time_elapsed > timedelta(minutes=exam_room.duration_minutes):
        # Auto-submit if time expired
        submission.status = SubmissionStatus.AUTO_SUBMITTED
        submission.submitted_at = datetime.utcnow()
        submission.time_taken_seconds = int(time_elapsed.total_seconds())
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam time has expired"
        )
    
    # Validate question belongs to this exam
    question = db.query(Question).filter(
        Question.id == answer.question_id,
        Question.exam_room_id == submission.exam_room_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found in this exam"
        )
    
    # Validate option belongs to this question
    if answer.selected_option_id:
        option = db.query(Option).filter(
            Option.id == answer.selected_option_id,
            Option.question_id == answer.question_id
        ).first()
        
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Option not found for this question"
            )
    
    # Check if answer already exists
    existing_answer = db.query(Answer).filter(
        Answer.submission_id == submission_id,
        Answer.question_id == answer.question_id
    ).first()
    
    if existing_answer:
        # Update existing answer
        existing_answer.selected_option_id = answer.selected_option_id
        if answer.selected_option_id:
            existing_answer.is_correct = option.is_correct if option else False
        else:
            existing_answer.is_correct = False
        db.commit()
        db.refresh(existing_answer)
        return existing_answer
    else:
        # Create new answer
        is_correct = option.is_correct if answer.selected_option_id and option else False
        db_answer = Answer(
            submission_id=submission_id,
            question_id=answer.question_id,
            selected_option_id=answer.selected_option_id,
            is_correct=is_correct
        )
        db.add(db_answer)
        db.commit()
        db.refresh(db_answer)
        return db_answer

@router.post("/{submission_id}/submit", response_model=SubmissionResult)
def submit_submission(
    submission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Check if user owns this submission
    if submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if submission is still active
    if submission.status != SubmissionStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission is already submitted"
        )
    
    # Calculate score and finalize submission
    answers = db.query(Answer).filter(Answer.submission_id == submission_id).all()
    total_score = sum(1 for answer in answers if answer.is_correct)
    
    # Get question marks for accurate scoring
    for answer in answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        if answer.is_correct and question:
            total_score += question.marks - 1  # Add the actual marks (subtracting the base 1)
    
    # Update submission
    submission.status = SubmissionStatus.SUBMITTED
    submission.submitted_at = datetime.utcnow()
    submission.total_score = total_score
    submission.time_taken_seconds = int((datetime.utcnow() - submission.started_at).total_seconds())
    
    db.commit()
    
    # Format results
    answer_results = []
    for answer in answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        correct_option = db.query(Option).filter(
            Option.question_id == answer.question_id,
            Option.is_correct == True
        ).first()
        
        answer_results.append(AnswerResult(
            question_id=answer.question_id,
            selected_option_id=answer.selected_option_id,
            correct_option_id=correct_option.id if correct_option else None,
            is_correct=answer.is_correct
        ))
    
    return SubmissionResult(
        submission_id=submission_id,
        total_score=total_score,
        status=submission.status.value,
        answers=answer_results
    )

@router.get("/my-history", response_model=List[SubmissionHistoryResponse])
def get_my_submission_history(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    submissions = db.query(Submission).filter(
        Submission.student_id == current_user.id
    ).order_by(Submission.started_at.desc()).offset(skip).limit(limit).all()
    
    # Format with exam room titles
    history = []
    for submission in submissions:
        exam_room = db.query(ExamRoom).filter(ExamRoom.id == submission.exam_room_id).first()
        history.append(SubmissionHistoryResponse(
            id=submission.id,
            exam_room_id=submission.exam_room_id,
            exam_room_title=exam_room.title if exam_room else "Unknown",
            total_score=submission.total_score,
            status=submission.status.value,
            started_at=submission.started_at,
            submitted_at=submission.submitted_at,
            time_taken_seconds=submission.time_taken_seconds
        ))
    
    return history

@router.get("/exam-room/{exam_room_id}/submissions", response_model=List[SubmissionHistoryResponse])
def get_exam_room_submissions(
    exam_room_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if exam room exists and user has permission
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == exam_room_id).first()
    if not exam_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam room not found"
        )
    
    # Only admin or creator can view submissions
    if current_user.role != "ADMIN" and exam_room.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    submissions = db.query(Submission).filter(
        Submission.exam_room_id == exam_room_id
    ).order_by(Submission.started_at.desc()).offset(skip).limit(limit).all()
    
    # Format with exam room titles
    history = []
    for submission in submissions:
        history.append(SubmissionHistoryResponse(
            id=submission.id,
            exam_room_id=submission.exam_room_id,
            exam_room_title=exam_room.title,
            total_score=submission.total_score,
            status=submission.status.value,
            started_at=submission.started_at,
            submitted_at=submission.submitted_at,
            time_taken_seconds=submission.time_taken_seconds
        ))
    
    return history
