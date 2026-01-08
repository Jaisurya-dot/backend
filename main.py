from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime
import os

# Import database configuration
from db.db_config import engine, Base

# Import models to ensure they are registered with Base
from models.user import User
from models.exam_room import ExamRoom
from models.question import Question, Option
from models.submission import Submission, Answer

# Import routers
from routes.auth import router as auth_router
from routes.user import router as user_router
from routes.exam_room import router as exam_room_router
from routes.question import router as question_router
from routes.submission import router as submission_router

from middleware import LoggingMiddleware, ErrorHandlingMiddleware

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quiz Master API",
    description="API for Quiz Management System",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Include Routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(exam_room_router)
app.include_router(question_router)
app.include_router(submission_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger("uvicorn")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Log to a file we can definitely read
    with open("C:/Users/JaisuryaSelvam/Desktop/MY_TECH/Full_Stack/backend/validation_errors.log", "a") as f:
        f.write(f"--- 422 Error at {datetime.now()} ---\n")
        f.write(f"URL: {request.url}\n")
        f.write(f"Errors: {str(errors)}\n\n")
    
    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
