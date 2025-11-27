from sqlmodel import Session, select, func
from app.models import User, UserScore, Submission
from typing import List, Dict
import asyncio
from fastapi import WebSocket, WebSocketDisconnect

class LeaderboardService:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast_leaderboard(self, session: Session):
        leaderboard = self.get_leaderboard(session)
        for connection in self.active_connections:
            try:
                await connection.send_json(leaderboard)
            except:
                pass
    
    def get_leaderboard(self, session: Session) -> List[Dict]:
        # note: subquery is implemented to consider only problems with score > 0
        solved_subquery = (
            select(
                UserScore.user_id,
                func.count(UserScore.problem_id).label("problems_solved")
            )
            .where(UserScore.best_score > 0)
            .group_by(UserScore.user_id)
            .subquery()
        )
        
        query = (
            select(
                User.user_id,
                User.username,
                func.coalesce(func.sum(UserScore.best_score), 0).label("total_score"),
                func.coalesce(solved_subquery.c.problems_solved, 0).label("problems_solved")
            )

            .select_from(User)
            .outerjoin(UserScore, User.user_id == UserScore.user_id)
            .outerjoin(solved_subquery, User.user_id == solved_subquery.c.user_id)
            .group_by(User.user_id, User.username, solved_subquery.c.problems_solved)
            .order_by(func.coalesce(func.sum(UserScore.best_score), 0).desc())
        )
        
        results = session.exec(query).all()
        
        leaderboard = []
        for rank, (user_id, username, total_score, problems_solved) in enumerate(results, 1):
            leaderboard.append({
                "rank": rank,
                "user_id": user_id,
                "username": username,
                "total_score": total_score,
                "problems_solved": problems_solved
            })
        
        return leaderboard

# this is the GLOBAL instance
leaderboard_service = LeaderboardService()