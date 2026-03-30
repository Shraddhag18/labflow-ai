from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud
from api.schemas.schemas import LogCreate, LogOut

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/", response_model=LogOut, status_code=201)
def create_log(body: LogCreate, db: Session = Depends(get_db)):
    return crud.create_log(db, title=body.title, content=body.content, team=body.team)


@router.get("/", response_model=list[LogOut])
def list_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_logs(db, skip=skip, limit=limit)


@router.get("/{log_id}", response_model=LogOut)
def get_log(log_id: int, db: Session = Depends(get_db)):
    log = crud.get_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
