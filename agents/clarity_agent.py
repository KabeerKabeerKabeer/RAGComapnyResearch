from state import ResearchState
from schemas.clarity_schema import ClarityOutput
from prompts.clarity_prompt import CLARITY_PROMPT
from config import groq_llm
from utils.logger import clarity_logger
from langchain_core.messages import HumanMessage, AIMessage
import json

def clarity_agent(state: ResearchState) -> ResearchState:
	"""
	Clarity Agent: Determines if the user query is sufficiently specific.
	
	Returns:
		Updated state with clarity_status, company_name, and clarification_question
	"""
	clarity_logger.info("=" * 50)
	clarity_logger.info("[ClarityAgent] Starting query analysis")
	
	# Get current query and conversation history
	user_query = state["user_query"]
	messages = state.get("messages", [])
	
	# ISOLATION FIX: Build history context safely to avoid Groq 6000 TPM limit
	history_text = ""
	
	# Grab only the last 3 messages to keep the context window tiny
	recent_messages = messages[-4:-1] if len(messages) > 1 else []
	
	for msg in recent_messages:
		if isinstance(msg, HumanMessage):
			history_text += f"User: {msg.content}\n"
		elif isinstance(msg, AIMessage):
			# Truncate AI messages so giant generated reports don't crash the router
			content = msg.content[:200] + "... [REPORT TRUNCATED]" if len(msg.content) > 200 else msg.content
			history_text += f"Assistant: {content}\n"
	
	# Format prompt
	prompt = CLARITY_PROMPT.format(
		history=history_text if history_text else "No previous conversation",
		query=user_query
	)
	
	clarity_logger.info(f"[ClarityAgent] Analyzing query: {user_query}")
	
	# Invoke LLM with structured output
	try:
		response = groq_llm.with_structured_output(ClarityOutput).invoke([HumanMessage(content=prompt)])
		
		clarity_logger.info(f"[ClarityAgent] Status: {response.clarity_status}")
		
		if response.company_name:
			clarity_logger.info(f"[ClarityAgent] Identified company: {response.company_name}")
		
		if response.clarification_question:
			clarity_logger.info(f"[ClarityAgent] Clarification needed: {response.clarification_question}")
		
		# Update state
		return {
			**state,
			"clarity_status": response.clarity_status,
			"company_name": response.company_name,
			"clarification_question": response.clarification_question
		}
		
	except Exception as e:
		clarity_logger.error(f"[ClarityAgent] Error: {str(e)}")
		# Fallback: assume needs clarification
		return {
			**state,
			"clarity_status": "needs_clarification",
			"clarification_question": "Could you please specify which company or entity you'd like me to research?"
		}