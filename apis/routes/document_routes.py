from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from apis.models.db_models.db_document_model import DBDocument
from apis.models.local_models.document_model import DocumentCreate, DocumentResponse
from apis.config.database import get_db
from constants.paths import DocumentRoutes, prefix
from apis.services.rag_service import ingest_document


router = APIRouter(prefix=prefix, tags=["Documents"])
        

router.post(DocumentRoutes.UPLOAD, response_model = DocumentResponse)
def create_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    new_doc = DBDocument(**doc.model_dump())
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # Ingest the document text into Chroma vector database
    ingest_document(new_doc.file_path, new_doc.file_type)
    
    return new_doc