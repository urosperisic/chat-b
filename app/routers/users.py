# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from .. import models, schemas, auth, database

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schemas.UserOut])
def read_users(
        skip: int = 0,
        limit: int = 100,
        current_admin: models.User = Depends(auth.get_current_admin_user),
        db: Session = Depends(get_db)
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user_id: UUID,
        current_admin: models.User = Depends(auth.get_current_admin_user),
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Brisemo korisnika i njegove poruke
    db.query(models.Message).filter(models.Message.user_id == user.id).delete()
    db.delete(user)
    db.commit()
    return
