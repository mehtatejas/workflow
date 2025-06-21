from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
from models import Workflow, ProcessMaster, Requirement
from schemas import WorkflowResultUpdate
from db import get_session
from typing import List

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.get("/", response_model=List[Workflow])
def list_workflows(session: Session = Depends(get_session)):
    return session.exec(select(Workflow)).all()

@router.get("/{workflow_id}", response_model=Workflow)
def get_workflow(workflow_id: UUID, session: Session = Depends(get_session)):
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return workflow

@router.put("/{workflow_id}", response_model=Workflow)
def submit_workflow_result(workflow_id: UUID, update: WorkflowResultUpdate, session: Session = Depends(get_session)):
    workflow = session.get(Workflow, workflow_id)
    if not workflow or workflow.status != "new":
        raise HTTPException(status_code=404, detail="Workflow not found or not in 'new' status.")
    if update.status not in ("complete", "failed"):
        raise HTTPException(status_code=400, detail="Invalid status.")
    workflow.process_result = update.process_result
    workflow.status = update.status
    workflow.updated_by = "system"
    workflow.updated_at = datetime.utcnow()
    session.add(workflow)
    session.commit()
    if update.status == "complete":
        all_steps = session.exec(select(ProcessMaster).order_by(ProcessMaster.process_order)).all()
        req_workflows = session.exec(select(Workflow).where(Workflow.requirement_id == workflow.requirement_id)).all()
        if len(req_workflows) == len(all_steps):
            from models import Requirement  # avoid circular import
            requirement = session.get(Requirement, workflow.requirement_id)
            if requirement:
                requirement.status = "done"
                requirement.updated_by = "system"
                requirement.updated_at = datetime.utcnow()
                session.add(requirement)
                session.commit()
    session.refresh(workflow)
    return workflow
