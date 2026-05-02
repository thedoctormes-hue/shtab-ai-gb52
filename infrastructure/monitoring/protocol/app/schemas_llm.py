"""
Pydantic models for LLM responses validation.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional


class SemanticVector(BaseModel):
    task: float = 0.0
    idea: float = 0.0
    identity: float = 0.0
    knowledge: float = 0.0
    pattern: float = 0.0


class Emotion(BaseModel):
    positive: float = 0.0
    negative: float = 0.0
    neutral: float = 1.0

    @validator('positive', 'negative', 'neutral')
    def check_range(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Value must be between 0.0 and 1.0, got {v}")
        return v


class FragmentClassification(BaseModel):
    semantic_vector: SemanticVector = Field(default_factory=SemanticVector)
    emotion: Emotion = Field(default_factory=Emotion)
    three_interpretations: List[str] = Field(default_factory=lambda: ["—", "—", "—"])
    conflict_detected: bool = False
    unknown_type: bool = False
    people: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    summary: str = "Классификация недоступна"
    confidence: float = 0.0
    meta: dict = Field(default_factory=dict)


class PatternAnalysis(BaseModel):
    description: str
    is_new: bool = True
