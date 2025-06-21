from config import settings
from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager

engine = create_engine(settings.database_url, echo=settings.sql_debug)

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
