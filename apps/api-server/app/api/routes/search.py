from fastapi import APIRouter
from pydantic import BaseModel

from app.services.search import search_service

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10


class SearchHit(BaseModel):
    document_id: str
    chunk_index: int
    content: str
    filename: str
    score: float


class SearchResponse(BaseModel):
    hits: list[SearchHit]
    total: int


@router.post("", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    results = await search_service.search(request.query, top_k=request.top_k)
    hits = [SearchHit(**r) for r in results]
    return SearchResponse(hits=hits, total=len(hits))
