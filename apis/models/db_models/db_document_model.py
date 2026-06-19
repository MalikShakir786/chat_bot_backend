from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from .base import Base


class DBDocument(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    file_type = Column(String)
    file_path = Column(Text)
    file_size = Column(String)
    uploaded_at = Column(DateTime, default=datetime.now)