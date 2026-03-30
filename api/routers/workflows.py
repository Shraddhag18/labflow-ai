import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from config import get_settings
from db.database import get_db
from db import crud
from api.schemas.schemas import WorkflowRunRequest, WorkflowRunResponse, AgentQueryRequest, AgentQueryResponse
from agent.core import AgentCore
from agent.tool_registry import TOOL_REGISTRY

logger = logging.getLogger("labflow.workflows")
router = APIRouter(prefix="/workflows", tags=["workflows"])

settings = get_settings()


def get_agent() -> AgentCore:
    """Dependency — returns a shared AgentCore instance."""
    return AgentCore()


@router.get("/")
def list_workflows():
    """Return all available workflow names and descriptions."""
    return [
        {"name": name, "description": spec["description"]}
        for name, spec in TOOL_REGISTRY.items()
    ]


@router.post("/run", response_model=WorkflowRunResponse)
def run_workflow(
    body: WorkflowRunRequest,
    db: Session = Depends(get_db),
    agent: AgentCore = Depends(get_agent),
):
    if body.workflow_name not in TOOL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown workflow '{body.workflow_name}'. "
                   f"Valid options: {list(TOOL_REGISTRY.keys())}",
        )

    # Validate payload has at least one non-empty string value
    if not body.payload or not any(
        isinstance(v, str) and v.strip() for v in body.payload.values()
    ):
        raise HTTPException(
            status_code=422,
            detail="Payload must contain at least one non-empty text field.",
        )

    try:
        output = agent.run_workflow(
            workflow_name=body.workflow_name,
            payload=body.payload,
            session_id=body.session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Workflow '%s' failed: %s", body.workflow_name, exc, exc_info=True)
        raise HTTPException(
            status_code=502,
            detail="Workflow execution failed. Check server logs for details.",
        )

    try:
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
        crud.record_ab_result(
            db,
            workflow_name=body.workflow_name,
            variant=output["variant"],
            quality_score=output["quality_score"],
        )
    except Exception as exc:
        logger.error("Failed to persist workflow run: %s", exc, exc_info=True)
        # Still return the result even if persistence fails
        return WorkflowRunResponse(
            run_id=-1,
            workflow_name=body.workflow_name,
            result=output["result"],
            variant=output["variant"],
            quality_score=output["quality_score"],
            latency_ms=output["latency_ms"],
            input_tokens=output["input_tokens"],
            output_tokens=output["output_tokens"],
        )

    logger.info(
        "Workflow '%s' complete — variant=%s score=%.2f latency=%dms",
        body.workflow_name, run.prompt_variant, run.quality_score or 0, run.latency_ms or 0,
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
def run_agent(
    body: AgentQueryRequest,
    agent: AgentCore = Depends(get_agent),
):
    """Agentic endpoint — model decides which tool(s) to call."""
    if not body.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    try:
        output = agent.run_agent(
            user_message=body.message,
            context_logs=body.context_logs,
        )
    except Exception as exc:
        logger.error("Agent run failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=502,
            detail="Agent execution failed. Check server logs for details.",
        )

    return AgentQueryResponse(**output)
