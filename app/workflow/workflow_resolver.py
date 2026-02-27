from .langchain_basic import LangchainBasicWorkflow
from .base_workflow import BaseWorkflow
from app.core.exceptions import AcHttpException

def resolve(workflow_id: str) -> type[BaseWorkflow] :
    if workflow_id == "langchain_basic":
        return LangchainBasicWorkflow
    else:
        raise AcHttpException("INVALID_WORKFLOW_ID", detail=f"Invalid workflow ID: {workflow_id}")
    