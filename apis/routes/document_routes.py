import os
from fastapi import Depends, APIRouter, UploadFile, File
from sqlalchemy.orm import Session

from apis.models.db_models.db_document_model import DBDocument
from apis.models.local_models.api_response_model import ApiResponse
from apis.config.database import get_db
from apis.models.local_models.document_model import DocumentResponse
from apis.utils.utils import format_file_size
from constants.paths import DocumentRoutes, prefix, files_storage
from apis.services.rag_service import ingest_document
import apis.utils.exceptions as exc

router = APIRouter(prefix=prefix, tags=["Documents"])


# Upload Document
@router.post(DocumentRoutes.UPLOAD, response_model=ApiResponse)
def create_document(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        os.makedirs(files_storage, exist_ok=True)

        file_path = os.path.join(files_storage, file.filename)

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        file_ext = os.path.splitext(file.filename)[1].lstrip(".")
        file_size = format_file_size(os.path.getsize(file_path))

        new_doc = DBDocument(
            user_id=user_id,
            filename=file.filename,
            file_type=file_ext,
            file_path=file_path,
            file_size=file_size
        )

        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        ingest_document(new_doc.file_path, new_doc.file_type)

        return ApiResponse(
            success=True,
            message="Document uploaded successfully",
            data=DocumentResponse.model_validate(new_doc)
        )

    except Exception as e:
        raise exc.AppException(
            status_code=500,
            message=f"Upload failed: {str(e)}",
            error_code="UPLOAD_ERROR"
        )

# Get All Documents
@router.get(DocumentRoutes.GET_ALL, response_model=ApiResponse)
def get_all_documents(
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        documents = (
            db.query(DBDocument)
            .filter(DBDocument.user_id == user_id)
            .order_by(DBDocument.uploaded_at.desc())
            .all()
        )

        return ApiResponse(
            success=True,
            message="Documents fetched successfully",
            data=[
                DocumentResponse.model_validate(doc)
                for doc in documents
            ]
        )

    except Exception as e:
        raise exc.AppException(
            status_code=500,
            message=f"Failed to fetch documents: {str(e)}",
            error_code="GET_ALL_ERROR"
        )

# Delete Document
@router.delete(DocumentRoutes.DELETE, response_model=ApiResponse)
def delete_document(
    id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        document = db.query(DBDocument).filter(
            DBDocument.id == id,
            DBDocument.user_id == user_id
        ).first()

        if not document:
            raise exc.NotFoundException(
                message="Document not found",
                error_code="DOCUMENT_NOT_FOUND"
            )

        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        db.delete(document)
        db.commit()

        return ApiResponse(
            success=True,
            message="Document deleted successfully",
            data={"document_id": id}
        )

    except exc.NotFoundException:
        raise

    except Exception as e:
        raise exc.AppException(
            status_code=500,
            message=f"Delete failed: {str(e)}",
            error_code="DELETE_ERROR"
        )