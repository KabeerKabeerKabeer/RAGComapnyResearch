from state import ResearchState
from schemas.reflection_schema import ReflectionOutput
from prompts.reflection_prompt import REFLECTION_PROMPT
from config import llm
from utils.logger import reflection_logger
from langchain_core.messages import HumanMessage
import json


def reflection_agent(state: ResearchState) -> ResearchState:
    """
    Reflection Agent: Self-evaluates research quality before synthesis.
    
    Returns:
        Updated state with reflection_notes
    """
    reflection_logger.info("=" * 50)
    reflection_logger.info("[ReflectionAgent] Starting self-evaluation")
    
    query = state.get("user_query", "")
    company = state.get("company_name", "")
    findings = state.get("research_findings", [])
    confidence = state.get("confidence_score", 0)
    validation = state.get("validation_result", "unknown")
    
    reflection_logger.info(f"[ReflectionAgent] Evaluating research on: {company}")
    reflection_logger.info(f"[ReflectionAgent] Confidence: {confidence}/10")
    reflection_logger.info(f"[ReflectionAgent] Validation: {validation}")
    
    # Format findings for prompt
    findings_text = json.dumps(findings, indent=2)
    
    # Build prompt
    prompt = REFLECTION_PROMPT.format(
        query=query,
        company=company,
        findings=findings_text,
        confidence=confidence,
        validation=validation
    )
    
    # Invoke LLM with structured output
    try:
        response = llm.with_structured_output(ReflectionOutput).invoke([HumanMessage(content=prompt)])
        
        reflection_logger.info(f"[ReflectionAgent] Reflection complete")
        reflection_logger.info(f"[ReflectionAgent] Notes preview: {response.reflection_notes[:150]}...")
        
        return {
            **state,
            "reflection_notes": response.reflection_notes
        }
        
    except Exception as e:
        reflection_logger.error(f"[ReflectionAgent] Error: {str(e)}")
        
        # Fallback reflection
        fallback_notes = f"""
        Self-evaluation: Research completed with confidence score of {confidence}/10.
        Validation status: {validation}.
        Findings cover {len(findings)} categories.
        Ready to proceed with synthesis.
        """
        
        return {
            **state,
            "reflection_notes": fallback_notes.strip()
        }
