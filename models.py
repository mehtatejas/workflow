from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Literal
from sqlmodel import SQLModel, Field

class ProcessMaster(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    type: str
    description: str
    process_prompt: str
    analysis_prompt: str
    process_order: int
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime

class Requirement(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    text: str
    priority: Optional[Literal["P1","P2","P3","P4","P5"]] = None
    status: Literal["new","approved","rejected","done"] = "new"
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime

class Workflow(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    requirement_id: UUID = Field(foreign_key="requirement.id")
    process_id: UUID = Field(foreign_key="processmaster.id")
    prompt: str
    process_result: Optional[str] = None
    status: Literal["new","complete","failed"] = "new"
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime
