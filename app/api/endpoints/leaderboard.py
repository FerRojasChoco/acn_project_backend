from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.leaderboard import leaderboard_service

router = APIRouter()

# get current leaderboard (HTTP endpoint)
@router.get("/")
def get_leaderboard(session: Session = Depends(get_session)):
    return leaderboard_service.get_leaderboard(session)

# get specific user's rank and details
@router.get("/user/{user_id}")
def get_user_rank(
    user_id: int,
    session: Session = Depends(get_session)
):
    leaderboard = leaderboard_service.get_leaderboard(session)
    
    user_rank = None
    for entry in leaderboard:
        if entry["user_id"] == user_id:
            user_rank = entry
            break
    
    if not user_rank:
        return {"error": "User not found in leaderboard"}
    
    return user_rank