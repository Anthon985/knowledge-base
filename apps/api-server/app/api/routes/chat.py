from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag import rag_service

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5


class SourceRef(BaseModel):
    filename: str
    document_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceRef]


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = await rag_service.chat(request.query, top_k=request.top_k)
    return ChatResponse(
        answer=result["answer"],
        sources=[SourceRef(**s) for s in result["sources"]],
    )
