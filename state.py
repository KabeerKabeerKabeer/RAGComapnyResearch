from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage
from typing_extensions import Annotated
from langgraph.graph.message import add_messages


class ResearchState(TypedDict):
    """
    Complete state schema for the multi-agent research system.
    Uses TypedDict for type safety and structured state management.
    """
    
    # Conversation history with automatic message aggregation
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Raw user query as received
    user_query: str
    
    # Clarified query after potential interrupt
    clarified_query: Optional[str]
    
    # Extracted company/entity name
    company_name: Optional[str]
    
    # Clarity agent output: "clear" or "needs_clarification"
    clarity_status: Optional[str]
    
    # Question to ask user if clarification needed
    clarification_question: Optional[str]
    
    # Research findings from search tools
    research_findings: Optional[List[Dict[str, Any]]]
    
    # Source metadata with URLs and titles
    sources: Optional[List[Dict[str, str]]]
    
    # Confidence score 0-10
    confidence_score: Optional[int]
    
    # Validation result: "sufficient" or "insufficient"
    validation_result: Optional[str]
    
    # Topics identified as missing by validator
    missing_topics: Optional[List[str]]
    
    # Retry counter for research loops
    attempts: int
    
    # Reflection agent's self-evaluation notes
    reflection_notes: Optional[str]
    
    # Final synthesized response
    final_response: Optional[str]
