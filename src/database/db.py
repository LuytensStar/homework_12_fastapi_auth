from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = 'postgresql+psycopg2://postgres:123732@localhost:50000/postgres'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False,bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
