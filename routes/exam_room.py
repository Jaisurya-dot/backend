from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from db.db_config import get_db
from models.exam_room import ExamRoom
from models.user import User
from schemas.exam_room import ExamRoomCreate, ExamRoomUpdate, ExamRoomResponse, ExamRoomWithQuestions
from core.auth import get_current_active_user, require_admin

router = APIRouter(prefix="/exam-rooms", tags=["exam-rooms"])

@router.post("/", response_model=ExamRoomResponse)
def create_exam_room(
    exam_room: ExamRoomCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Validate end_time is after start_time
    if exam_room.end_time <= exam_room.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    db_exam_room = ExamRoom(
        **exam_room.dict(),
        created_by=current_user.id
    )
    db.add(db_exam_room)
    db.commit()
    db.refresh(db_exam_room)
    return db_exam_room

@router.get("/", response_model=List[ExamRoomResponse])
def get_exam_rooms(
    skip: int = 0,
    limit: int = 100,
    published_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(ExamRoom)
    
    if published_only:
        query = query.filter(ExamRoom.is_published == True)
    
    exam_rooms = query.offset(skip).limit(limit).all()
    return exam_rooms

@router.get("/my-exams", response_model=List[ExamRoomResponse])
def get_my_exam_rooms(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    exam_rooms = db.query(ExamRoom).filter(
        ExamRoom.created_by == current_user.id
    ).offset(skip).limit(limit).all()
    return exam_rooms

@router.get("/{exam_room_id}", response_model=ExamRoomWithQuestions)
def get_exam_room_by_id(
    exam_room_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == exam_room_id).first()
    if not exam_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam room not found"
        )
    
    # Check if user has access (admin or creator)
    if current_user.role != "ADMIN" and exam_room.created_by != current_user.id:
        if not exam_room.is_published:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return exam_room

@router.put("/{exam_room_id}", response_model=ExamRoomResponse)
def update_exam_room(
    exam_room_id: int,
    exam_room_update: ExamRoomUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == exam_room_id).first()
    if not exam_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam room not found"
        )
    
    # Check if user is the creator or admin
    if exam_room.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or admin can update this exam room"
        )
    
    # Validate end_time is after start_time if both are provided
    update_data = exam_room_update.dict(exclude_unset=True)
    if "start_time" in update_data and "end_time" in update_data:
        if update_data["end_time"] <= update_data["start_time"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )
    
    for field, value in update_data.items():
        setattr(exam_room, field, value)
    
    db.commit()
    db.refresh(exam_room)
    return exam_room

@router.delete("/{exam_room_id}")
def delete_exam_room(
    exam_room_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == exam_room_id).first()
    if not exam_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam room not found"
        )
    
    # Check if user is the creator or admin
    if exam_room.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or admin can delete this exam room"
        )
    
    db.delete(exam_room)
    db.commit()
    return {"message": "Exam room deleted successfully"}

@router.post("/{exam_room_id}/publish")
def publish_exam_room(
    exam_room_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    exam_room = db.query(ExamRoom).filter(ExamRoom.id == exam_room_id).first()
    if not exam_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam room not found"
        )
    
    # Check if user is the creator or admin
    if exam_room.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or admin can publish this exam room"
        )
    
    exam_room.is_published = True
    db.commit()
    db.refresh(exam_room)
    return {"message": "Exam room published successfully"}
