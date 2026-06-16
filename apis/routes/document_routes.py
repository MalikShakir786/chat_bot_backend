import os
from typing import List
from fastapi import Depends, APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from apis.models.db_models.db_document_model import DBDocument
from apis.models.local_models.api_response_model import ApiResponse
from apis.config.database import get_db
from constants.paths import DocumentRoutes, prefix, files_storage
from apis.services.rag_service import ingest_document

router = APIRouter(prefix=prefix, tags=["Documents"])


# Upload Document
@router.post(DocumentRoutes.UPLOAD, response_model=ApiResponse)
def create_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        os.makedirs(files_storage, exist_ok=True)

        file_path = os.path.join(files_storage, file.filename)

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        file_ext = os.path.splitext(file.filename)[1].lstrip(".")

        new_doc = DBDocument(
            filename=file.filename, file_type=file_ext, file_path=file_path
        )

        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        ingest_document(new_doc.file_path, new_doc.file_type)

        return ApiResponse(
            success=True, message="Document uploaded successfully", data=new_doc
        )

    except Exception as e:
        return ApiResponse(
            success=False, message="Document upload failed", error_code="UPLOAD_ERROR", data=None
        )


# Get All Documents
@router.get(DocumentRoutes.GET_ALL, response_model=ApiResponse)
def get_all_documents(db: Session = Depends(get_db)):
    try:
        documents = db.query(DBDocument).all()

        data = [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_path": doc.file_path,
                "uploaded_at": doc.uploaded_at
            }
            for doc in documents
        ]

        return ApiResponse(
            success=True,
            message="Documents fetched successfully",
            data=data
        )

    except Exception as e:
        print("GET_ALL_ERROR:", str(e))  # for debugging

        return ApiResponse(
            success=False,
            message="Failed to fetch documents",
            error_code="GET_ALL_ERROR",
            data=None
        )


# Delete Document
@router.delete(DocumentRoutes.DELETE, response_model=ApiResponse)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    try:
        document = db.query(DBDocument).filter(DBDocument.id == document_id).first()

        if not document:
            return ApiResponse(
            success=False,
            message="Document not found",
            error_code="DOCUMENT_NOT_FOUND",
            data=None
            )

        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        db.delete(document)
        db.commit()

        return ApiResponse(
            success=True,
            message="Document deleted successfully",
            data={"document_id": document_id},
        )

    except Exception:
        return ApiResponse(
            success=False,
            message="Failed to delete document",
            error_code="DELETE_ERROR",
            data=None
        )
