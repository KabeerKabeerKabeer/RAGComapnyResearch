from pydantic import BaseModel, Field
from typing import List


class ValidatorOutput(BaseModel):
    """
    Structured output schema for Validator Agent.
    Assesses research sufficiency and identifies gaps.
    """
    
    validation_result: str = Field(
        description='Must be either "sufficient" or "insufficient"'
    )
    
    missing_topics: List[str] = Field(
        default_factory=list,
        description="List of missing or incomplete research categories"
    )
    
    validator_notes: str = Field(
        description="Detailed assessment of research quality and gaps"
    )
