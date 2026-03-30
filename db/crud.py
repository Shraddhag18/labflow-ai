from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models import ResearchLog, WorkflowRun, ABTestRecord


# ── Research Logs ────────────────────────────────────────────────────────────

def create_log(db: Session, title: str, content: str, team: str = "General") -> ResearchLog:
    log = ResearchLog(title=title, content=content, team=team)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_log(db: Session, log_id: int) -> ResearchLog | None:
    return db.query(ResearchLog).filter(ResearchLog.id == log_id).first()


def list_logs(db: Session, skip: int = 0, limit: int = 50) -> list[ResearchLog]:
    return db.query(ResearchLog).order_by(ResearchLog.created_at.desc()).offset(skip).limit(limit).all()


# ── Workflow Runs ─────────────────────────────────────────────────────────────

def create_run(
    db: Session,
    workflow_name: str,
    result: dict,
    log_id: int | None = None,
    prompt_variant: str = "A",
    quality_score: float | None = None,
    latency_ms: int | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
) -> WorkflowRun:
    run = WorkflowRun(
        workflow_name=workflow_name,
        log_id=log_id,
        result=result,
        prompt_variant=prompt_variant,
        quality_score=quality_score,
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def list_runs(db: Session, skip: int = 0, limit: int = 100) -> list[WorkflowRun]:
    return db.query(WorkflowRun).order_by(WorkflowRun.created_at.desc()).offset(skip).limit(limit).all()


def get_run_metrics(db: Session) -> dict:
    total = db.query(func.count(WorkflowRun.id)).scalar()
    avg_latency = db.query(func.avg(WorkflowRun.latency_ms)).scalar()
    avg_quality = db.query(func.avg(WorkflowRun.quality_score)).scalar()

    per_workflow = (
        db.query(WorkflowRun.workflow_name, func.count(WorkflowRun.id))
        .group_by(WorkflowRun.workflow_name)
        .all()
    )

    return {
        "total_runs": total or 0,
        "avg_latency_ms": round(avg_latency or 0, 1),
        "avg_quality_score": round(avg_quality or 0, 2),
        "runs_per_workflow": {name: count for name, count in per_workflow},
    }


# ── A/B Test Records ──────────────────────────────────────────────────────────

def record_ab_result(db: Session, workflow_name: str, variant: str, quality_score: float) -> ABTestRecord:
    record = ABTestRecord(workflow_name=workflow_name, variant=variant, quality_score=quality_score)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_ab_results(db: Session) -> list[dict]:
    rows = (
        db.query(
            ABTestRecord.workflow_name,
            ABTestRecord.variant,
            func.avg(ABTestRecord.quality_score).label("avg_score"),
            func.count(ABTestRecord.id).label("sample_count"),
        )
        .group_by(ABTestRecord.workflow_name, ABTestRecord.variant)
        .all()
    )
    return [
        {
            "workflow_name": r.workflow_name,
            "variant": r.variant,
            "avg_score": round(r.avg_score, 3),
            "sample_count": r.sample_count,
        }
        for r in rows
    ]
