from fastapi import FastAPI
from db import create_db_and_tables
from api.requirements import router as requirements_router
from api.workflows import router as workflows_router
from api.processes import router as processes_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(requirements_router)
app.include_router(workflows_router)
app.include_router(processes_router)
