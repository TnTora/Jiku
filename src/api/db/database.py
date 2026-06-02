from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import redis
import os

redisdb = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    # echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db
