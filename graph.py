from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from state import ResearchState
from agents.clarity_agent import clarity_agent
from agents.research_agent import research_agent
from agents.validator_agent import validator_agent
from agents.reflection_agent import reflection_agent
from agents.synthesis_agent import synthesis_agent
from memory.checkpoint import get_checkpointer
from config import MAX_RETRY_ATTEMPTS, CONFIDENCE_THRESHOLD
from utils.logger import graph_logger


def create_research_graph(checkpointer: BaseCheckpointSaver = None) -> StateGraph:
    """
    Create the multi-agent research workflow graph.
    
    Graph Architecture:
        START
          ↓
        Clarity Agent
          ↓
        [Decision: needs_clarification?]
          ↓ NO
        Research Agent
          ↓
        [Decision: confidence >= 6?]
          ↓ YES          ↓ NO
      Reflection     Validator Agent
          ↓              ↓
      Synthesis    [Decision: insufficient AND attempts < 3?]
          ↓              ↓ YES         ↓ NO
        END      Research Agent    Reflection Agent
                       ↓                ↓
                   (loop back)      Synthesis Agent
                                        ↓
                                      END
    """
    
    # Create the graph
    builder = StateGraph(ResearchState)
    
    # Add all agent nodes
    graph_logger.info("[Graph] Adding agent nodes")
    builder.add_node("clarity_agent", clarity_agent)
    builder.add_node("research_agent", research_agent)
    builder.add_node("validator_agent", validator_agent)
    builder.add_node("reflection_agent", reflection_agent)
    builder.add_node("synthesis_agent", synthesis_agent)
    
    # Set entry point
    builder.set_entry_point("clarity_agent")
    
    # Add conditional edges
    graph_logger.info("[Graph] Adding conditional routing logic")
    
    # Clarity -> Research or Interrupt
    def route_after_clarity(state: ResearchState) -> str:
        clarity_status = state.get("clarity_status")
        
        if clarity_status == "needs_clarification":
            graph_logger.info("[Routing] Clarity -> INTERRUPT (clarification needed)")
            return "interrupt"
        else:
            graph_logger.info("[Routing] Clarity -> Research")
            return "research_agent"
    
    builder.add_conditional_edges(
        "clarity_agent",
        route_after_clarity,
        {
            "interrupt": END,  # Will interrupt and wait for user input
            "research_agent": "research_agent"
        }
    )
    
    # Research -> Validator or Reflection
    def route_after_research(state: ResearchState) -> str:
        confidence = state.get("confidence_score", 0)
        
        if confidence >= CONFIDENCE_THRESHOLD:
            graph_logger.info(f"[Routing] Research -> Reflection (confidence={confidence} >= {CONFIDENCE_THRESHOLD})")
            return "reflection_agent"
        else:
            graph_logger.info(f"[Routing] Research -> Validator (confidence={confidence} < {CONFIDENCE_THRESHOLD})")
            return "validator_agent"
    
    builder.add_conditional_edges(
        "research_agent",
        route_after_research,
        {
            "validator_agent": "validator_agent",
            "reflection_agent": "reflection_agent"
        }
    )
    
    # Validator -> Research (retry) or Reflection (max attempts)
    def route_after_validation(state: ResearchState) -> str:
        validation = state.get("validation_result")
        attempts = state.get("attempts", 0)
        
        if validation == "insufficient" and attempts < MAX_RETRY_ATTEMPTS:
            graph_logger.info(f"[Routing] Validator -> Research (retry {attempts}/{MAX_RETRY_ATTEMPTS})")
            return "research_agent"
        else:
            if attempts >= MAX_RETRY_ATTEMPTS:
                graph_logger.info(f"[Routing] Validator -> Reflection (max attempts reached)")
            else:
                graph_logger.info(f"[Routing] Validator -> Reflection (validation sufficient)")
            return "reflection_agent"
    
    builder.add_conditional_edges(
        "validator_agent",
        route_after_validation,
        {
            "research_agent": "research_agent",
            "reflection_agent": "reflection_agent"
        }
    )
    
    # Reflection -> Synthesis
    builder.add_edge("reflection_agent", "synthesis_agent")
    
    # Synthesis -> END
    builder.add_edge("synthesis_agent", END)
    
    # Compile graph with checkpointer
    if checkpointer is None:
        checkpointer = get_checkpointer()
    
    graph = builder.compile(
        checkpointer=checkpointer
    )
    
    graph_logger.info("[Graph] Graph compiled successfully")
    
    return graph


def get_graph():
    """Get compiled research graph with default checkpointer."""
    return create_research_graph()
