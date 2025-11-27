from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.leaderboard import leaderboard_service

router = APIRouter()

#note: show to Pablo
@router.websocket("/ws/leaderboard")
async def websocket_leaderboard(websocket: WebSocket, session: Session = Depends(get_session)):
    await leaderboard_service.connect(websocket)
    try:
        # send initial leaderboard when client connects
        leaderboard = leaderboard_service.get_leaderboard(session)
        await websocket.send_json(leaderboard)
        
        # keep connection alive - wait for client messages
        while True:
            data = await websocket.receive_text()
            # client can send "refresh" to get latest leaderboard
            if data == "refresh":
                leaderboard = leaderboard_service.get_leaderboard(session)
                await websocket.send_json(leaderboard)
                
    except WebSocketDisconnect:
        leaderboard_service.disconnect(websocket)