from fastapi import APIRouter
from pydantic import BaseModel

from app.services.workflow import workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


class WorkflowStatusResponse(BaseModel):
    name: str
    phase: str
    started_at: str | None
    finished_at: str | None


@router.get("/{workflow_name}", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_name: str):
    result = await workflow_service.get_workflow_status(workflow_name)
    return WorkflowStatusResponse(**result)
