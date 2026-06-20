from sqlalchemy import Column, Integer, String
from apis.models.db_models.base import Base


class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)