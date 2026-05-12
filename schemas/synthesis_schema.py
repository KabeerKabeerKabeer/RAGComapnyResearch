from pydantic import BaseModel, Field


class SynthesisOutput(BaseModel):
    """
    Structured output schema for Synthesis Agent.
    Generates final polished response with citations.
    """
    
    final_response: str = Field(
        description="Complete, well-organized research report with citations"
    )
