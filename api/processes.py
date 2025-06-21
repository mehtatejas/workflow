from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlmodel import Session, select
from models import ProcessMaster
from db import get_session
from typing import List

router = APIRouter(prefix="/processes", tags=["processes"])

@router.get("/", response_model=List[ProcessMaster])
def list_processes(session: Session = Depends(get_session)):
    return session.exec(select(ProcessMaster)).all()

@router.get("/{process_id}", response_model=ProcessMaster)
def get_process(process_id: UUID, session: Session = Depends(get_session)):
    process = session.get(ProcessMaster, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="ProcessMaster not found.")
    return process
