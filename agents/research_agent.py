from state import ResearchState
from schemas.research_schema import ResearchOutput
from prompts.research_prompt import RESEARCH_PROMPT
from config import llm
from utils.logger import research_logger, search_logger
from tools.tavily_search import TavilySearch
from tools.duckduckgo_search import DuckDuckGoSearch
from langchain_core.messages import HumanMessage
import json


def research_agent(state: ResearchState) -> ResearchState:
    """
    Research Agent: Performs external research using search tools.
    
    Returns:
        Updated state with research_findings, sources, and confidence_score
    """
    research_logger.info("=" * 50)
    research_logger.info("[ResearchAgent] Starting research")
    
    company = state.get("company_name") or state.get("clarified_query", "")
    attempt = state.get("attempts", 0) + 1
    missing_topics = state.get("missing_topics", [])
    
    research_logger.info(f"[ResearchAgent] Company: {company}")
    research_logger.info(f"[ResearchAgent] Attempt: {attempt}/3")
    
    if missing_topics:
        research_logger.info(f"[ResearchAgent] Focusing on missing topics: {missing_topics}")
    
    # Generate search queries
    queries = generate_search_queries(company, missing_topics, attempt)
    research_logger.info(f"[ResearchAgent] Generated {len(queries)} search queries")
    
    # Perform searches with fallback strategy
    search_results = perform_searches(queries)
    
    if not search_results:
        research_logger.error("[ResearchAgent] No search results obtained")
        return {
            **state,
            "attempts": attempt,
            "research_findings": [],
            "sources": [],
            "confidence_score": 0
        }
    
    research_logger.info(f"[ResearchAgent] Obtained {len(search_results)} total results")
    
    # Format search results for prompt
    search_text = format_search_results(search_results)
    
    # Build prompt
    prompt = RESEARCH_PROMPT.format(
        company=company,
        search_results=search_text,
        missing_topics=", ".join(missing_topics) if missing_topics else "None",
        attempt=attempt
    )
    
    # Invoke LLM with structured output
    try:
        response = llm.with_structured_output(ResearchOutput).invoke([HumanMessage(content=prompt)])
        
        research_logger.info(f"[ResearchAgent] Confidence Score: {response.confidence_score}/10")
        research_logger.info(f"[ResearchAgent] Extracted {len(response.findings)} findings")
        research_logger.info(f"[ResearchAgent] Tracked {len(response.sources)} sources")
        
        return {
            **state,
            "attempts": attempt,
            "research_findings": response.findings,
            "sources": response.sources,
            "confidence_score": response.confidence_score
        }
        
    except Exception as e:
        research_logger.error(f"[ResearchAgent] Error processing results: {str(e)}")
        
        # Fallback: create minimal findings from raw results
        fallback_findings = []
        fallback_sources = []
        
        for result in search_results[:5]:
            fallback_findings.append({
                "category": "General Information",
                "information": result.get("content", "")[:500],
                "source_title": result.get("title", ""),
                "source_url": result.get("url", "")
            })
            fallback_sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:300],
                "published_date": result.get("published_date")
            })
        
        return {
            **state,
            "attempts": attempt,
            "research_findings": fallback_findings,
            "sources": fallback_sources,
            "confidence_score": 3  # Low confidence for fallback
        }


def generate_search_queries(company: str, missing_topics: list, attempt: int) -> list:
    """Generate dynamic search queries based on company and missing topics."""
    
    base_queries = [
        f"{company} company overview",
        f"{company} CEO founder",
        f"{company} latest news 2024 2025",
        f"{company} financial revenue",
        f"{company} competitors market position"
    ]
    
    # Add targeted queries for missing topics
    if missing_topics:
        for topic in missing_topics:
            if "financial" in topic.lower():
                base_queries.append(f"{company} revenue earnings funding")
            elif "leadership" in topic.lower() or "CEO" in topic:
                base_queries.append(f"{company} CEO executive team")
            elif "news" in topic.lower() or "development" in topic.lower():
                base_queries.append(f"{company} recent developments announcements")
            elif "competitor" in topic.lower():
                base_queries.append(f"{company} main competitors industry")
    
    return base_queries


def perform_searches(queries: list) -> list:
    """
    Perform searches using Tavily with DuckDuckGo fallback.
    """
    # Try Tavily first
    tavily = TavilySearch()
    results = tavily.multi_search(queries, max_results=3)
    
    if results:
        return results
    
    # Fallback to DuckDuckGo
    search_logger.warning("[SearchFallback] Tavily failed, switching to DuckDuckGo")
    ddg = DuckDuckGoSearch()
    results = ddg.multi_search(queries, max_results=3)
    
    return results


def format_search_results(results: list) -> str:
    """Format search results for LLM consumption."""
    formatted = []
    
    for i, result in enumerate(results, 1):
        formatted.append(f"""
Result {i}:
Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Content: {result.get('content', 'N/A')[:500]}...
Published: {result.get('published_date', 'N/A')}
---
""")
    
    return "\n".join(formatted)
