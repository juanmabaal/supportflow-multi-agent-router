from typing import Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["low", "medium", "high"]

class EvaluationResult(BaseModel):
    relevance: int = Field(ge=1, le=10)
    completeness: int = Field(ge=1, le=10)
    accuracy: int = Field(ge=1, le=10)
    groundedness: int = Field(ge=1, le=10)
    clarity: int = Field(ge=1, le=10)
    overall_score: float = Field(ge=1, le=10)
    passed: bool
    risk_level: RiskLevel
    reason: str
    improvement_suggestions: list[str] = Field(default_factory=list)