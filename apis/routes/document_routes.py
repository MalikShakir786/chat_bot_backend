from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from apis.models.db_models.db_document_model import DBDocument
from apis.models.local_models.document_model import DocumentCreate, DocumentResponse
from config import get_db
from constants.paths import DocumentRoutes, prefix


router = APIRouter(prefix=prefix, tags=["Documents"])
        

router.post(DocumentRoutes.UPLOAD, response_model = DocumentResponse)
def create_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    new_doc = DBDocument(**doc.model_dump())
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc