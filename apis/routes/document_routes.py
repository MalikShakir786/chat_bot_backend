import os
from fastapi import Depends, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from apis.models.db_models.db_document_model import DBDocument
from apis.models.local_models.document_model import DocumentResponse
from apis.config.database import get_db
from constants.paths import DocumentRoutes, prefix
from apis.services.rag_service import ingest_document


router = APIRouter(prefix=prefix, tags=["Documents"])
        

@router.post(DocumentRoutes.UPLOAD, response_model = DocumentResponse)
def create_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Create uploads directory if not exists
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 2. Save uploaded file to disk
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
        
    # 3. Determine file type from extension
    file_ext = os.path.splitext(file.filename)[1].lstrip('.')
    
    # 4. Save metadata to PostgreSQL DB
    new_doc = DBDocument(
        filename=file.filename,
        file_type=file_ext,
        file_path=file_path
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # 5. Ingest the document text into Chroma vector database
    ingest_document(new_doc.file_path, new_doc.file_type)
    
    return new_doc