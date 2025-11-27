from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_current_user
from app.models import Submission, User, SubmissionStatus, Problem
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class SubmissionCreate(BaseModel):
    problem_id: int
    code: str

@router.get("/")
def get_submissions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get only current user's submissions
    submissions = session.exec(
        select(Submission)
        .where(Submission.user_id == current_user.user_id)
        .order_by(Submission.submitted_at.desc())
    ).all()
    return submissions

@router.get("/{submission_id}")
def get_submission(
    submission_id: int, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Check if user owns this submission
    if submission.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return submission


@router.post("/")
def create_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new submission and return its ID for judging"""
    
    problem = session.get(Problem, submission_data.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    submission = Submission(
        user_id=current_user.user_id,
        problem_id=submission_data.problem_id,
        code=submission_data.code,
        status=SubmissionStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    
    session.add(submission)
    session.commit()
    session.refresh(submission)
    
    return {
        "submission_id": submission.submission_id,
        "status": submission.status,
        "message": "Submission created. Use /judge/{submission_id}/judge to start judging."
    }