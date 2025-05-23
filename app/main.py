# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import auth, users, messages, ws
from app.database import Base, engine

# Kreiraj tabele u bazi (za sada bez Alembic migracija)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✳️ Exception handler za 422 greške (RequestValidationError)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("🔴 VALIDATION ERROR:")
    print("🔗 Path:", request.url.path)
    print("📥 Body:", exc.body)
    print("❌ Errors:", exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

# CORS konfiguracija - dozvoljava frontend na localhost:5173 da pristupa API-ju
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registruj rute
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(messages.router)
app.include_router(ws.router)

@app.get("/")
def root():
    return {"message": "Welcome to the chat API"}
