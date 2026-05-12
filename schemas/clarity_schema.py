from pydantic import BaseModel, Field
from typing import Optional


class ClarityOutput(BaseModel):
    """
    Structured output schema for Clarity Agent.
    Determines if query is clear enough to proceed with research.
    """
    
    clarity_status: str = Field(
        description='Must be either "clear" or "needs_clarification"'
    )
    
    company_name: Optional[str] = Field(
        default=None,
        description="The identified company or entity name if query is clear"
    )
    
    clarification_question: Optional[str] = Field(
        default=None,
        description="Question to ask user if clarification is needed"
    )
