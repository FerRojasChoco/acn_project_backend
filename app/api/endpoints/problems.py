from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_current_user
from app.models import Problem, User

router = APIRouter()

@router.get("/")
def get_problems(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    problems = session.exec(select(Problem)).all()
    return problems

@router.get("/{problem_id}")
def get_problem(
    problem_id: int, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    problem = session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")    
    return problem
