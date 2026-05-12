from pydantic import BaseModel, Field
from typing import List, Dict


class ResearchOutput(BaseModel):
    """
    Structured output schema for Research Agent.
    Contains aggregated research findings with confidence assessment.
    """
    
    findings: List[Dict] = Field(
        description="List of research findings with categorized information"
    )
    
    confidence_score: int = Field(
        ge=0,
        le=10,
        description="Confidence score from 0-10 based on research quality"
    )
    
    sources: List[Dict] = Field(
        description="List of sources with title, url, and content"
    )
