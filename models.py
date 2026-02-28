from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URI = os.getenv('DATABASE_URI')
engine = create_engine(DATABASE_URI, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    tg_chat_id = Column(Integer)
    yt_auth = Column(Boolean, default=False)
    vk_group_id = Column(Integer)

def init_db():
    Base.metadata.create_all(bind=engine)

