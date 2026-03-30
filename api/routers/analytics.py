from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud
from agent.prompts.variants import VARIANT_B_IMPROVEMENTS

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    return crud.get_run_metrics(db)


@router.get("/ab-results")
def get_ab_results(db: Session = Depends(get_db)):
    raw = crud.get_ab_results(db)

    # Group by workflow and compute improvement
    grouped: dict[str, dict] = {}
    for row in raw:
        wf = row["workflow_name"]
        if wf not in grouped:
            grouped[wf] = {}
        grouped[wf][row["variant"]] = {
            "avg_score": row["avg_score"],
            "sample_count": row["sample_count"],
        }

    results = []
    for wf, variants in grouped.items():
        a_score = variants.get("A", {}).get("avg_score", 0)
        b_score = variants.get("B", {}).get("avg_score", 0)
        improvement = VARIANT_B_IMPROVEMENTS.get(wf, 0)
        results.append({
            "workflow_name": wf,
            "variant_a": variants.get("A"),
            "variant_b": variants.get("B"),
            "documented_improvement_pct": round(improvement * 100, 1),
            "observed_improvement_pct": round((b_score - a_score) / max(a_score, 0.01) * 100, 1) if a_score else None,
        })

    return results


@router.get("/runs")
def list_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    runs = crud.list_runs(db, skip=skip, limit=limit)
    return [
        {
            "id": r.id,
            "workflow_name": r.workflow_name,
            "variant": r.prompt_variant,
            "quality_score": r.quality_score,
            "latency_ms": r.latency_ms,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]
