import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres_user_default")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres_password_default")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres_db_default")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres") 

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}" 

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_tables():
    Base.metadata.create_all(bind=engine)

def reset_users_table():
    with engine.begin() as conn:
        conn.execute(text('DROP TABLE IF EXISTS users CASCADE;'))
    Base.metadata.create_all(bind=engine)

def reset_all_tables():
    # Drop all tables then recreate according to current models
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)