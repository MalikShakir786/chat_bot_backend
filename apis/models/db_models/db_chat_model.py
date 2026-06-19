from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from .base import Base


class DBChat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    query = Column(Text)
    answer = Column(Text)
    sources = Column(Text)          # JSON-serialized list of source dicts
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.now)