from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.conf.config import settings

DATABASE_URL = settings.sqlalchemy_database_url


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False,bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
