# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


# 🧾 JWT token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    role: Optional[str] = None


# 👤 Korisnik (registracija / unos)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    country: str


# 👤 Korisnik (čitamo iz baze ili vraćamo ka frontu)
class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    country: str
    role: str

    class Config:
        orm_mode = True


# 📝 Poruka (unos nove poruke)
class MessageCreate(BaseModel):
    content: str


# 📝 Poruka (prikaz)
class MessageOut(BaseModel):
    id: UUID
    content: str
    timestamp: datetime
    owner: UserOut

    class Config:
        orm_mode = True
