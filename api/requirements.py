from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
from models import Requirement, ProcessMaster, Workflow
from schemas import (
    RequirementCreate,
    RequirementApprove,
    WorkflowAdvanceResponse,
    WorkflowResultUpdate,
)
from db import get_session
from typing import List

router = APIRouter(prefix="/requirements", tags=["requirements"])

@router.post("/", response_model=Requirement, status_code=status.HTTP_201_CREATED)
def create_requirement(req: RequirementCreate, session: Session = Depends(get_session)):
    now = datetime.utcnow()
    requirement = Requirement(
        text=req.text,
        status="new",
        created_by="system",
        created_at=now,
        updated_by="system",
        updated_at=now
    )
    session.add(requirement)
    session.commit()
    session.refresh(requirement)
    return requirement

@router.put("/{requirement_id}/approve", response_model=Requirement)
def approve_requirement(requirement_id: UUID, req: RequirementApprove, session: Session = Depends(get_session)):
    requirement = session.get(Requirement, requirement_id)
    if not requirement or requirement.status != "new":
        raise HTTPException(status_code=404, detail="Requirement not found or not in 'new' status.")
    requirement.text = req.text
    requirement.priority = req.priority
    requirement.status = "approved"
    requirement.updated_by = "system"
    requirement.updated_at = datetime.utcnow()
    session.add(requirement)
    session.commit()
    session.refresh(requirement)
    return requirement

@router.post("/{requirement_id}/advance", response_model=WorkflowAdvanceResponse, status_code=status.HTTP_201_CREATED)
def advance_workflow(requirement_id: UUID, session: Session = Depends(get_session)):
    requirement = session.get(Requirement, requirement_id)
    if not requirement or requirement.status != "approved":
        raise HTTPException(status_code=404, detail="Requirement not found or not approved.")
    process_steps = session.exec(select(ProcessMaster).order_by(ProcessMaster.process_order)).all()
    if not process_steps:
        raise HTTPException(status_code=400, detail="No process steps defined.")
    completed_process_ids = [w.process_id for w in session.exec(select(Workflow).where(Workflow.requirement_id == requirement_id)).all()]
    next_step = next((p for p in process_steps if p.id not in completed_process_ids), None)
    if not next_step:
        raise HTTPException(status_code=400, detail="No steps remain.")
    prior_workflows = session.exec(select(Workflow).where(Workflow.requirement_id == requirement_id).order_by(Workflow.created_at)).all()
    history = "\n".join(f"- {w.process_result}" for w in prior_workflows if w.process_result)
    prompt = f"{next_step.process_prompt}\n{requirement.text}"
    if history:
        prompt += f"\nHistory:\n{history}"
    process_result = f"MOCKED LLM RESPONSE for: {prompt[:50]}..."
    now = datetime.utcnow()
    workflow = Workflow(
        requirement_id=requirement_id,
        process_id=next_step.id,
        prompt=prompt,
        process_result=process_result,
        status="new",
        created_by="system",
        created_at=now,
        updated_by="system",
        updated_at=now
    )
    session.add(workflow)
    session.commit()
    session.refresh(workflow)
    return WorkflowAdvanceResponse(
        workflow_id=workflow.id,
        prompt=prompt,
        process_result=process_result
    )

@router.get("/", response_model=List[Requirement])
def list_requirements(session: Session = Depends(get_session)):
    return session.exec(select(Requirement)).all()

@router.get("/{requirement_id}", response_model=Requirement)
def get_requirement(requirement_id: UUID, session: Session = Depends(get_session)):
    requirement = session.get(Requirement, requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found.")
    return requirement
