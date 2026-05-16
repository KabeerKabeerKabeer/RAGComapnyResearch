from typing import Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError
from langchain_core.messages import HumanMessage
from config import groq_llm
from utils.logger import get_logger

logger = get_logger("ParserRetry")

T = TypeVar('T', bound=BaseModel)


def parse_with_retry(
    response_text: str,
    schema: Type[T],
    agent_name: str
) -> Optional[T]:
    """
    Attempt to parse LLM response with retry on failure.
    
    Args:
        response_text: Raw LLM output text
        schema: Pydantic schema to parse into
        agent_name: Name of agent for logging
        
    Returns:
        Parsed schema object or None if all attempts fail
    """
    
    # First attempt: direct parsing
    try:
        parsed = schema.model_validate_json(response_text)
        logger.info(f"[{agent_name}] Successful parse on first attempt")
        return parsed
    except (ValidationError, Exception) as e:
        logger.warning(f"[{agent_name}] Parse failed: {str(e)}")
        logger.info(f"[{agent_name}] Attempting repair with formatting prompt")
        
    # Second attempt: retry with repair prompt
    try:
        repair_prompt = f"""
The following JSON output was malformed. Please fix it and return ONLY valid JSON that matches this schema:

{schema.model_json_schema()}

Malformed output:
{response_text}

Return ONLY the corrected JSON, no explanation.
"""
        
        repair_response = groq_llm.invoke([HumanMessage(content=repair_prompt)])
        repaired_text = repair_response.content
        
        parsed = schema.model_validate_json(repaired_text)
        logger.info(f"[{agent_name}] Successful parse after repair")
        return parsed
        
    except (ValidationError, Exception) as e:
        logger.error(f"[{agent_name}] Parse failed after retry: {str(e)}")
        return None


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON from text that may contain markdown code blocks.
    
    Args:
        text: Raw text that may contain ```json blocks
        
    Returns:
        Cleaned JSON string
    """
    # Remove markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    
    return text.strip()
