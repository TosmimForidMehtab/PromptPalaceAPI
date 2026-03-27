from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.api.v1 import prompts, auth
from api.db.database import engine
from api.models import user, prompt
from sqlmodel import SQLModel
from api.core.auth_middleware import AuthMiddleware
from api.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    SQLModel.metadata.create_all(bind=engine)
    # Optionally: connect to other services
    yield
    # Shutdown logic (optional)
    # e.g. engine.dispose(), close redis, etc.


app = FastAPI(title="Prompt Marketplace API", lifespan=lifespan)

# AuthMiddleware must be added BEFORE CORSMiddleware
# This ensures CORS headers are added to ALL responses including auth errors
app.add_middleware(AuthMiddleware)

# Configure CORS with allowed origins from environment variable
# CORSMiddleware must be last to wrap all other middleware responses
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(prompts.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
