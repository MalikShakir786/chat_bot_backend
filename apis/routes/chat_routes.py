import json
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from apis.models.db_models.db_chat_model import DBChat
from apis.models.local_models.api_response_model import ApiResponse
from apis.config.database import get_db
from apis.models.local_models.chat_model import ChatRequest, ChatModel, SourceItem
from constants.paths import ChatRoutes, prefix
from apis.services.rag_service import query_documents
from apis.services.jwt_service import get_current_user
import apis.utils.exceptions as exc

router = APIRouter(prefix=prefix, tags=["Chat"])


# Send a chat message / query the RAG pipeline
@router.post(ChatRoutes.SEND_MESSAGE, response_model=ApiResponse)
def send_message(
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        result = query_documents(
            query=payload.query,
            top_k=payload.top_k,
            min_score=payload.min_score,
        )

        # Save chat first
        new_chat = DBChat(
            user_id=payload.user_id,
            query=payload.query,
            answer=result["answer"],
            sources=json.dumps(result["sources"]),
            confidence=result["confidence"],
        )

        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        # Build response using DB-generated ID
        chat_response = ChatModel(
            id=new_chat.id,
            user_id=payload.user_id,
            query=payload.query,
            answer=result["answer"],
            sources=[SourceItem(**s) for s in result["sources"]],
            confidence=result["confidence"],
            has_context=result["has_context"],
            created_at=new_chat.created_at
        )

        return ApiResponse(
            success=True,
            message="Query processed successfully",
            data=chat_response,
        )

    except Exception as e:
        raise exc.AppException(
            status_code=500,
            message=f"Failed to process query: {str(e)}",
            error_code="CHAT_ERROR"
        )

# Get chat history
@router.get(ChatRoutes.HISTORY, response_model=ApiResponse)
def get_chat_history(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        chats = (
            db.query(DBChat)
            .filter(DBChat.user_id == user_id)
            .order_by(DBChat.id.desc())
            .all()
        )

        data = [
            ChatModel(
                id=chat.id,
                user_id=chat.user_id,
                query=chat.query,
                answer=chat.answer,
                sources=[SourceItem(**s) for s in json.loads(chat.sources)],
                confidence=chat.confidence,
                created_at=chat.created_at
            )
            for chat in chats
        ]

        return ApiResponse(
            success=True,
            message="Chat history fetched successfully",
            data=data
        )

    except Exception as e:
        raise exc.AppException(
            status_code=500,
            message=f"Failed to fetch chat history: {str(e)}",
            error_code="CHAT_HISTORY_ERROR"
        )