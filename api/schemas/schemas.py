from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any


class LogCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=10)
    team: str = Field(default="General", max_length=100)


class LogOut(BaseModel):
    id: int
    title: str
    content: str
    team: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowRunRequest(BaseModel):
    workflow_name: str
    payload: dict[str, Any]
    log_id: int | None = None
    session_id: str | None = None


class WorkflowRunResponse(BaseModel):
    run_id: int
    workflow_name: str
    result: dict[str, Any]
    variant: str
    quality_score: float
    latency_ms: int
    input_tokens: int | None
    output_tokens: int | None


class AgentQueryRequest(BaseModel):
    message: str
    context_logs: str = ""


class AgentQueryResponse(BaseModel):
    agent_response: str | None
    tools_called: list[str]
    latency_ms: int
    input_tokens: int
    output_tokens: int
    session_id: str


class ABRecordRequest(BaseModel):
    workflow_name: str
    variant: str
    quality_score: float = Field(..., ge=0.0, le=1.0)
