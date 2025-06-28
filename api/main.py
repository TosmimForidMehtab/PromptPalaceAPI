from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.api.v1 import prompts, auth
from api.db.database import engine
from api.models import user, prompt
from sqlmodel import SQLModel
from api.core.auth_middleware import AuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    SQLModel.metadata.create_all(bind=engine)
    # Optionally: connect to other services
    yield
    # Shutdown logic (optional)
    # e.g. engine.dispose(), close redis, etc.


app = FastAPI(title="Prompt Marketplace API", lifespan=lifespan)

app.add_middleware(AuthMiddleware)
app.include_router(prompts.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
