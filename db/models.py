from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db.database import Base


class ResearchLog(Base):
    __tablename__ = "research_logs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    team = Column(String(100), default="General")
    created_at = Column(DateTime, default=datetime.utcnow)

    workflow_runs = relationship("WorkflowRun", back_populates="log", cascade="all, delete")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(100), nullable=False)
    log_id = Column(Integer, ForeignKey("research_logs.id"), nullable=True)
    result = Column(JSON, nullable=True)
    prompt_variant = Column(String(10), default="A")   # "A" or "B"
    quality_score = Column(Float, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    log = relationship("ResearchLog", back_populates="workflow_runs")


class ABTestRecord(Base):
    __tablename__ = "ab_test_records"

    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(100), nullable=False)
    variant = Column(String(10), nullable=False)   # "A" or "B"
    quality_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
