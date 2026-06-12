from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# url structure = postgresql://user:password@host:port/database
db_url = "postgresql://user:12345678@localhost:5432/chat_bot"

engine = create_engine(db_url)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

session = SessionLocal()


def get_db():
    db = session
    try:
        yield db
    finally: 
        db.close()