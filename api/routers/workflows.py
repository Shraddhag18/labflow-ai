from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud
from api.schemas.schemas import WorkflowRunRequest, WorkflowRunResponse, AgentQueryRequest, AgentQueryResponse
from agent.core import AgentCore
from agent.tool_registry import TOOL_REGISTRY

router = APIRouter(prefix="/workflows", tags=["workflows"])

_agent = AgentCore()


@router.get("/")
def list_workflows():
    """Return all available workflow names and descriptions."""
    return [
        {"name": name, "description": spec["description"]}
        for name, spec in TOOL_REGISTRY.items()
    ]


@router.post("/run", response_model=WorkflowRunResponse)
def run_workflow(body: WorkflowRunRequest, db: Session = Depends(get_db)):
    if body.workflow_name not in TOOL_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown workflow: {body.workflow_name}")

    output = _agent.run_workflow(
        workflow_name=body.workflow_name,
        payload=body.payload,
        session_id=body.session_id,
    )

    run = crud.create_run(
        db,
        workflow_name=body.workflow_name,
        result=output["result"],
        log_id=body.log_id,
        prompt_variant=output["variant"],
        quality_score=output["quality_score"],
        latency_ms=output["latency_ms"],
        input_tokens=output["input_tokens"],
        output_tokens=output["output_tokens"],
    )

    # Also record in AB test table
    crud.record_ab_result(
        db,
        workflow_name=body.workflow_name,
        variant=output["variant"],
        quality_score=output["quality_score"],
    )

    return WorkflowRunResponse(
        run_id=run.id,
        workflow_name=run.workflow_name,
        result=run.result,
        variant=run.prompt_variant,
        quality_score=run.quality_score,
        latency_ms=run.latency_ms,
        input_tokens=run.input_tokens,
        output_tokens=run.output_tokens,
    )


@router.post("/agent", response_model=AgentQueryResponse)
def run_agent(body: AgentQueryRequest):
    """Agentic endpoint — model decides which tool(s) to call."""
    output = _agent.run_agent(user_message=body.message, context_logs=body.context_logs)
    return AgentQueryResponse(**output)
