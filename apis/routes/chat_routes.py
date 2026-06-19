import json
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from apis.models.db_models.db_chat_model import DBChat
from apis.models.local_models.api_response_model import ApiResponse
from apis.config.database import get_db
from apis.models.local_models.chat_model import ChatRequest, ChatResponse, SourceItem
from constants.paths import ChatRoutes, prefix
from apis.services.rag_service import query_documents

router = APIRouter(prefix=prefix, tags=["Chat"])


# Send a chat message / query the RAG pipeline
@router.post(ChatRoutes.SEND_MESSAGE, response_model=ApiResponse)
def send_message(payload: ChatRequest, db: Session = Depends(get_db)):
    try:
        result = query_documents(
            query=payload.query,
            top_k=payload.top_k,
            min_score=payload.min_score,
        )

        chat_response = ChatResponse(
            query=payload.query,
            answer=result["answer"],
            sources=[SourceItem(**s) for s in result["sources"]],
            confidence=result["confidence"],
            has_context=result["has_context"],
        )

        new_chat = DBChat(
            query=payload.query,
            answer=result["answer"],
            sources=json.dumps(result["sources"]),
            confidence=result["confidence"],
        )

        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        return ApiResponse(
            success=True,
            message="Query processed successfully",
            data=chat_response,
        )

    except Exception as e:
        print(e)
        return ApiResponse(
            success=False,
            message="Failed to process query",
            error_code="CHAT_ERROR",
            data=None,
        )


# Get chat history
@router.get(ChatRoutes.HISTORY, response_model=ApiResponse)
def get_chat_history(db: Session = Depends(get_db)):
    try:
        chats = db.query(DBChat).order_by(DBChat.id.desc()).all()

        data = [
            {
                "id": chat.id,
                "query": chat.query,
                "answer": chat.answer,
                "sources": json.loads(chat.sources) if chat.sources else [],
                "confidence": chat.confidence,
                "created_at": chat.created_at,
            }
            for chat in chats
        ]

        return ApiResponse(
            success=True,
            message="Chat history fetched successfully",
            data=data,
        )

    except Exception as e:
        print("CHAT_HISTORY_ERROR:", str(e))

        return ApiResponse(
            success=False,
            message="Failed to fetch chat history",
            error_code="CHAT_HISTORY_ERROR",
            data=None,
        )