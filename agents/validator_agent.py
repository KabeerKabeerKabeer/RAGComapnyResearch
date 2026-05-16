from state import ResearchState
from schemas.validator_schema import ValidatorOutput
from prompts.validator_prompt import VALIDATOR_PROMPT
from config import groq_llm
from utils.logger import validator_logger
from langchain_core.messages import HumanMessage
import json


def validator_agent(state: ResearchState) -> ResearchState:
    """
    Validator Agent: Assesses research sufficiency and identifies gaps.
    
    Returns:
        Updated state with validation_result and missing_topics
    """
    validator_logger.info("=" * 50)
    validator_logger.info("[ValidatorAgent] Starting validation")
    
    query = state.get("user_query", "")
    company = state.get("company_name", "")
    findings = state.get("research_findings", [])
    confidence = state.get("confidence_score", 0)
    attempt = state.get("attempts", 0)
    
    validator_logger.info(f"[ValidatorAgent] Evaluating {len(findings)} findings")
    validator_logger.info(f"[ValidatorAgent] Current confidence: {confidence}/10")
    validator_logger.info(f"[ValidatorAgent] Attempt: {attempt}/3")
    
    # Format findings for prompt
    findings_text = json.dumps(findings, indent=2)
    
    # Build prompt
    prompt = VALIDATOR_PROMPT.format(
        query=query,
        company=company,
        findings=findings_text,
        confidence=confidence,
        attempt=attempt
    )
    
    # Invoke LLM with structured output
    try:
        response = groq_llm.with_structured_output(ValidatorOutput).invoke([HumanMessage(content=prompt)])
        
        validator_logger.info(f"[ValidatorAgent] Validation Result: {response.validation_result}")
        
        if response.missing_topics:
            validator_logger.info(f"[ValidatorAgent] Missing Topics: {', '.join(response.missing_topics)}")
        
        validator_logger.info(f"[ValidatorAgent] Notes: {response.validator_notes[:100]}...")
        
        return {
            **state,
            "validation_result": response.validation_result,
            "missing_topics": response.missing_topics
        }
        
    except Exception as e:
        validator_logger.error(f"[ValidatorAgent] Error: {str(e)}")
        
        # Fallback validation logic
        if confidence >= 6 and len(findings) >= 5:
            result = "sufficient"
            missing = []
        else:
            result = "insufficient"
            missing = ["additional details needed"]
        
        validator_logger.info(f"[ValidatorAgent] Fallback validation: {result}")
        
        return {
            **state,
            "validation_result": result,
            "missing_topics": missing
        }
