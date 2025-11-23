from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Submission

router = APIRouter()

@router.get("/")
def get_submissions(session: Session = Depends(get_session)):
    submissions = session.exec(select(Submission)).all()
    return submissions

@router.get("/{submission_id}")
def get_submission(submission_id: int, session: Session = Depends(get_session)):
    submission = session.get(Submission, submission_id)
    if not submission:
        return {"error": "Submission not found"}
    return submission
