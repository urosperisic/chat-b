import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError
from .. import auth, models, database

from ..websocket_manager import manager

router = APIRouter()


def get_current_user_sync(token: str, db: Session) -> models.User:
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = auth.get_user(db, user_id)
    if user is None:
        raise credentials_exception
    return user

@router.websocket("/ws/messages")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(database.get_db),
):
    # Prvo prihvati WebSocket konekciju
    await websocket.accept()

    # Ručno dohvati token iz query parametara
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    # Autentifikacija korisnika
    try:
        user = await asyncio.to_thread(get_current_user_sync, token, db)
    except HTTPException:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    print(f"User {user.email} connected via WebSocket")

    try:
        while True:
            data = await websocket.receive_text()
            new_message = models.Message(content=data, user_id=user.id)
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            message_out = {
                "id": str(new_message.id),
                "content": new_message.content,
                "timestamp": new_message.timestamp.isoformat(),
                "owner": {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "country": user.country,
                    "role": user.role.value,
                },
            }

            await manager.broadcast(message_out)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"User {user.email} disconnected from WebSocket")
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket error: {e}")
        await websocket.close()
