from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag.retriever import ContractRAGService
from app.api.deps import get_current_user

router = APIRouter(tags=["chat"])


@router.post("/versions/{vid}/chat", response_model=ChatResponse)
def ask_contract_question(
    vid: str,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    rag_service = ContractRAGService(db)
    result = rag_service.answer_question(
        version_id=vid,
        question=body.question,
        top_k=body.top_k,
        user_id=current_user.id,
    )
    return ChatResponse(**result)
