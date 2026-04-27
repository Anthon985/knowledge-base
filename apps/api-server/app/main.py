from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, documents, search, workflows
from app.config import settings
from app.db.session import engine
from app.models.document import Base
from app.services.search import search_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging

    logger = logging.getLogger(__name__)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        await search_service.ensure_index()
    except Exception as e:
        logger.warning(f"Elasticsearch not available at startup, will retry later: {e}")
    yield
    await search_service.close()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
