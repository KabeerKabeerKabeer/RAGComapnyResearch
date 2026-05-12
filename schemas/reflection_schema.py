from pydantic import BaseModel, Field


class ReflectionOutput(BaseModel):
    """
    Structured output schema for Reflection Agent.
    Self-evaluates research quality before synthesis.
    """
    
    reflection_notes: str = Field(
        description="Self-evaluation of research completeness, coherence, and quality"
    )
