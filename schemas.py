from pydantic import BaseModel, Field as PydanticField
from uuid import UUID
from typing import Optional, Literal

class RequirementCreate(BaseModel):
    text: str
    class Config:
        schema_extra = {"example": {"text": "Describe your requirement"}}

class RequirementApprove(BaseModel):
    text: str
    priority: Literal["P1","P2","P3","P4","P5"]
    class Config:
        schema_extra = {"example": {"text": "Updated your requirement", "priority": "P1"}}

class WorkflowResultUpdate(BaseModel):
    process_result: str
    status: Literal["complete", "failed"]
    class Config:
        schema_extra = {"example": {"process_result": "LLM response here", "status": "complete"}}

class WorkflowAdvanceResponse(BaseModel):
    workflow_id: UUID
    prompt: str
    process_result: str
