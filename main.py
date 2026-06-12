from fastapi import FastAPI
from apis.routes import router as task_router
import apis.models.db_models.db_document_model as dbModel
from apis.config.database import engine


app = FastAPI()

app.include_router(task_router)

dbModel.Base.metadata.create_all(bind=engine)