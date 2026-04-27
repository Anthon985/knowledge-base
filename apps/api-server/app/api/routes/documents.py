import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.document import Document, DocumentStatus
from app.services.storage import storage_service
from app.services.workflow import workflow_service

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    status: str
    chunk_count: int
    error_message: str | None
    workflow_name: str | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_data = await file.read()
    content_type = file.content_type or "application/octet-stream"

    storage_path = storage_service.upload_file(file_data, file.filename, content_type)

    doc = Document(
        filename=storage_path.split("/")[-1],
        original_filename=file.filename,
        content_type=content_type,
        file_size=len(file_data),
        storage_path=storage_path,
        status=DocumentStatus.PENDING,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    try:
        workflow_name = await workflow_service.submit_document_processing(
            document_id=str(doc.id),
            storage_path=storage_path,
        )
        doc.status = DocumentStatus.PROCESSING
        doc.workflow_name = workflow_name
        await db.commit()
        await db.refresh(doc)
    except Exception as e:
        doc.status = DocumentStatus.FAILED
        doc.error_message = f"Failed to submit workflow: {str(e)}"
        await db.commit()
        await db.refresh(doc)

    return _to_response(doc)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit)
    )
    documents = result.scalars().all()

    count_result = await db.execute(select(Document))
    total = len(count_result.scalars().all())

    return DocumentListResponse(
        documents=[_to_response(doc) for doc in documents],
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    result = await db.execute(select(Document).where(Document.id == doc_uuid))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _to_response(doc)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    result = await db.execute(select(Document).where(Document.id == doc_uuid))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        storage_service.delete_file(doc.storage_path)
    except Exception:
        pass

    await db.delete(doc)
    await db.commit()
    return {"message": "Document deleted"}


@router.get("/{document_id}/status")
async def get_document_status(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    result = await db.execute(select(Document).where(Document.id == doc_uuid))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    workflow_status = None
    if doc.workflow_name:
        try:
            workflow_status = await workflow_service.get_workflow_status(doc.workflow_name)
        except Exception:
            pass

    return {
        "document_status": doc.status.value,
        "workflow_status": workflow_status,
    }


def _to_response(doc: Document) -> DocumentResponse:
    return DocumentResponse(
        id=str(doc.id),
        filename=doc.filename,
        original_filename=doc.original_filename,
        content_type=doc.content_type,
        file_size=doc.file_size,
        status=doc.status.value,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message,
        workflow_name=doc.workflow_name,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
        updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
    )
