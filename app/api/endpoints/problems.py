from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Problem

router = APIRouter()

@router.get("/")
def get_problems(session: Session = Depends(get_session)):
    problems = session.exec(select(Problem)).all()
    return problems

@router.get("/{problem_id}")
def get_problem(problem_id: int, session: Session = Depends(get_session)):
    problem = session.get(Problem, problem_id)
    if not problem:
        return {"error": "Problem not found"}
    return problem
