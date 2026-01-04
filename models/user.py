from sqlalchemy import Column, DateTime, Enum, Integer, String
from db.db_config import  Base
from datetime import datetime
import enum

 

class UserRole(str, enum.Enum):
    """User roles for authentication"""
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"


class User(Base):
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False,  )
    email = Column(String(255), unique=True,  nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, name="userrole"), default=UserRole.STUDENT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
     
