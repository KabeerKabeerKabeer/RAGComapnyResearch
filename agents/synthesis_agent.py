from state import ResearchState
from schemas.synthesis_schema import SynthesisOutput
from prompts.synthesis_prompt import SYNTHESIS_PROMPT
from config import llm
from utils.logger import synthesis_logger
from langchain_core.messages import HumanMessage, AIMessage
import json


def synthesis_agent(state: ResearchState) -> ResearchState:
    """
    Synthesis Agent: Generates final polished response with citations.
    
    Returns:
        Updated state with final_response and updated messages
    """
    synthesis_logger.info("=" * 50)
    synthesis_logger.info("[SynthesisAgent] Creating final response")
    
    query = state.get("user_query", "")
    company = state.get("company_name", "")
    findings = state.get("research_findings", [])
    reflection = state.get("reflection_notes", "")
    sources = state.get("sources", [])
    
    synthesis_logger.info(f"[SynthesisAgent] Synthesizing research for: {company}")
    synthesis_logger.info(f"[SynthesisAgent] Using {len(findings)} findings and {len(sources)} sources")
    
    # Format data for prompt
    findings_text = json.dumps(findings, indent=2)
    sources_text = json.dumps(sources, indent=2)
    
    # Build prompt
    prompt = SYNTHESIS_PROMPT.format(
        query=query,
        company=company,
        findings=findings_text,
        reflection=reflection,
        sources=sources_text
    )
    
    # Invoke LLM with structured output
    try:
        response = llm.with_structured_output(SynthesisOutput).invoke([HumanMessage(content=prompt)])
        
        final_response = response.final_response
        
        synthesis_logger.info(f"[SynthesisAgent] Generated response ({len(final_response)} chars)")
        synthesis_logger.info("[SynthesisAgent] Synthesis complete")
        
        # Add AI message to conversation history
        messages = state.get("messages", [])
        messages.append(AIMessage(content=final_response))
        
        return {
            **state,
            "final_response": final_response,
            "messages": messages
        }
        
    except Exception as e:
        synthesis_logger.error(f"[SynthesisAgent] Error: {str(e)}")
        
        # Fallback: create basic response
        fallback_response = create_fallback_response(company, findings, sources)
        
        messages = state.get("messages", [])
        messages.append(AIMessage(content=fallback_response))
        
        return {
            **state,
            "final_response": fallback_response,
            "messages": messages
        }


def create_fallback_response(company: str, findings: list, sources: list) -> str:
    """Create a basic fallback response if synthesis fails."""
    
    response = f"# {company} Research Report\n\n"
    
    # Organize findings by category
    categories = {}
    for finding in findings:
        category = finding.get("category", "General Information")
        if category not in categories:
            categories[category] = []
        categories[category].append(finding)
    
    # Add sections for each category
    for category, items in categories.items():
        response += f"## {category}\n\n"
        for item in items:
            info = item.get("information", "")
            response += f"{info}\n\n"
    
    # Add sources
    if sources:
        response += "## Sources\n\n"
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Source")
            url = source.get("url", "")
            response += f"{i}. [{title}]({url})\n"
    
    return response
