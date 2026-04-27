import httpx

from app.config import settings


class WorkflowService:
    def __init__(self):
        self.server_url = settings.argo_server_url
        self.namespace = settings.argo_namespace

    async def submit_document_processing(
        self, document_id: str, storage_path: str
    ) -> str:
        workflow_spec = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {
                "generateName": "doc-processing-",
                "namespace": self.namespace,
            },
            "spec": {
                "entrypoint": "process-document",
                "arguments": {
                    "parameters": [
                        {"name": "document-id", "value": document_id},
                        {"name": "storage-path", "value": storage_path},
                    ]
                },
                "workflowTemplateRef": {
                    "name": "doc-processing-dag",
                },
            },
        }

        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            response = await client.post(
                f"{self.server_url}/api/v1/workflows/{self.namespace}",
                json={"workflow": workflow_spec},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            result = response.json()
            return result["metadata"]["name"]

    async def get_workflow_status(self, workflow_name: str) -> dict:
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            response = await client.get(
                f"{self.server_url}/api/v1/workflows/{self.namespace}/{workflow_name}",
            )
            response.raise_for_status()
            result = response.json()
            return {
                "name": result["metadata"]["name"],
                "phase": result["status"].get("phase", "Unknown"),
                "started_at": result["status"].get("startedAt"),
                "finished_at": result["status"].get("finishedAt"),
            }


workflow_service = WorkflowService()
