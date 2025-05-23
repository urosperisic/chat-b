from fastapi import APIRouter, Depends, HTTPException, status, Body, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import schemas, models, auth
from ..database import get_db
from ..websocket_manager import manager  # <-- importuj menadžera websocket konekcija
import json

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)

@router.post("/", response_model=schemas.MessageOut)
def create_message(
    message: schemas.MessageCreate = Body(...),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_message = models.Message(
        content=message.content,
        user_id=current_user.id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/", response_model=List[schemas.MessageOut])
def read_messages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    messages = db.query(models.Message)\
        .order_by(models.Message.timestamp.asc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return messages

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.user_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(message)
    db.commit()

    background_tasks.add_task(
        manager.broadcast,
        {"action": "delete", "id": str(message_id)}
    )

    return
