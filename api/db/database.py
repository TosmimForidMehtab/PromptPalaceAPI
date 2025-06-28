from sqlmodel import SQLModel, create_engine, Session
from api.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True,
)


def get_session():
    with Session(engine) as session:
        yield session
