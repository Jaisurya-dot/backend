from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from db.db_config import engine, Base
from models import user, exam_room, question, submission
from routes import auth, user, exam_room, question, submission
from middleware import LoggingMiddleware, ErrorHandlingMiddleware
from exceptions import QuizException

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quiz Backend - PostgreSQL",
    description="A comprehensive quiz management system with user authentication, exam rooms, questions, and submissions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Include all routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(exam_room.router)
app.include_router(question.router)
app.include_router(submission.router)

# Exception handler for custom exceptions
@app.exception_handler(QuizException)
async def quiz_exception_handler(request, exc: QuizException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "details": exc.details
        }
    )

@app.get("/")
def Get():
    return {
        "message": "Quiz Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}