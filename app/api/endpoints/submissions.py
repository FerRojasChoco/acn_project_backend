from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_current_user
from app.models import Submission, User, SubmissionStatus
from datetime import datetime

router = APIRouter()

@router.get("/")
def get_submissions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    submissions = session.exec(select(Submission)).all()
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
    return submission


@router.post("/")
def create_submission(
    problem_id: int,
    code: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    
    problem = session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    submission = Submission(
        user_id=current_user.user_id,
        problem_id=problem_id,
        code=code,
        status=SubmissionStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    
    session.add(submission)
    session.commit()
    session.refresh(submission)
    
    return submission