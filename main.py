from fastapi import FastAPI
from apis.routes.document_routes import router as document_router
from apis.routes.chat_routes import router as chat_router
from apis.config.database import engine
from apis.models.db_models.db_document_model import Base

app = FastAPI()

# Include both routers
app.include_router(document_router)
app.include_router(chat_router)

# Create tables
Base.metadata.create_all(bind=engine)