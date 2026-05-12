#!/usr/bin/env python3
"""
Multi-Agent Research Assistant - CLI Interface
Production-grade research system using LangGraph orchestration
"""

import sys
from langchain_core.messages import HumanMessage
from graph import get_graph
from utils.logger import get_logger
from state import ResearchState

logger = get_logger("CLI")


class ResearchAssistantCLI:
    """CLI interface for the multi-agent research assistant."""
    
    def __init__(self):
        self.graph = get_graph()
        self.thread_id = "default_conversation"
        self.config = {"configurable": {"thread_id": self.thread_id}}
        logger.info("[CLI] Research Assistant initialized")
    
    def run(self):
        """Main conversation loop."""
        print("\n" + "=" * 70)
        print("🔬 MULTI-AGENT RESEARCH ASSISTANT")
        print("=" * 70)
        print("\nWelcome! I'm a production-grade research system powered by LangGraph.")
        print("I use multiple specialized agents to conduct thorough research.\n")
        print("Commands:")
        print("  - Type your research query")
        print("  - Type 'exit' or 'quit' to end")
        print("  - Type 'reset' to start a new conversation")
        print("\n" + "=" * 70 + "\n")
        
        while True:
            try:
                # Get user input
                user_input = input("\n🧑 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit']:
                    print("\n👋 Goodbye!\n")
                    break
                
                if user_input.lower() == 'reset':
                    self.thread_id = f"conversation_{hash(str(user_input))}"
                    self.config = {"configurable": {"thread_id": self.thread_id}}
                    print("\n✅ Conversation reset. Starting fresh!\n")
                    continue
                
                # Process query
                self.process_query(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                logger.error(f"[CLI] Error: {str(e)}")
                print(f"\n❌ Error: {str(e)}\n")
    
    def process_query(self, query: str):
        """Process a user query through the agent graph."""
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "user_query": query,
            "clarified_query": None,
            "company_name": None,
            "clarity_status": None,
            "clarification_question": None,
            "research_findings": None,
            "sources": None,
            "confidence_score": None,
            "validation_result": None,
            "missing_topics": None,
            "attempts": 0,
            "reflection_notes": None,
            "final_response": None
        }
        
        logger.info(f"[CLI] Processing query: {query}")
        print("\n🤖 Assistant: Let me research that for you...\n")
        
        # Stream through the graph
        try:
            for event in self.graph.stream(initial_state, self.config):
                self.handle_event(event)
            
            # Check if we need clarification (interrupted)
            state = self.graph.get_state(self.config)
            
            if state.values.get("clarity_status") == "needs_clarification":
                clarification_q = state.values.get("clarification_question")
                print(f"\n🤔 {clarification_q}\n")
                
                # Get clarification from user
                clarification = input("🧑 You: ").strip()
                
                if clarification:
                    # Update state and resume
                    self.resume_with_clarification(clarification)
        
        except Exception as e:
            logger.error(f"[CLI] Processing error: {str(e)}")
            print(f"\n❌ An error occurred: {str(e)}\n")
    
    def resume_with_clarification(self, clarification: str):
        """Resume graph execution after receiving clarification."""
        
        logger.info(f"[CLI] Resuming with clarification: {clarification}")
        
        # Update the state with clarification
        current_state = self.graph.get_state(self.config)
        
        updated_state = {
            **current_state.values,
            "clarified_query": clarification,
            "company_name": clarification,  # Use clarification as company name
            "clarity_status": "clear",
            "messages": current_state.values["messages"] + [HumanMessage(content=clarification)]
        }
        
        # Resume from research_agent
        try:
            for event in self.graph.stream(updated_state, self.config):
                self.handle_event(event)
        except Exception as e:
            logger.error(f"[CLI] Resume error: {str(e)}")
            print(f"\n❌ An error occurred: {str(e)}\n")
    
    def handle_event(self, event: dict):
        """Handle streaming events from the graph."""
        
        for node_name, node_state in event.items():
            if node_name == "synthesis_agent":
                # Display final response
                final_response = node_state.get("final_response")
                if final_response:
                    print(f"\n{final_response}\n")
            
            elif node_name == "research_agent":
                attempt = node_state.get("attempts", 0)
                confidence = node_state.get("confidence_score", 0)
                print(f"   🔍 Research complete (attempt {attempt}, confidence: {confidence}/10)")
            
            elif node_name == "validator_agent":
                validation = node_state.get("validation_result")
                if validation == "insufficient":
                    missing = node_state.get("missing_topics", [])
                    print(f"   ⚠️  Validation: need more info on {', '.join(missing)}")
            
            elif node_name == "reflection_agent":
                print(f"   💭 Reflecting on research quality...")


def main():
    """Main entry point."""
    
    # Check for required environment variables
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY not found in .env file")
        print("Please add your Groq API key to the .env file")
        sys.exit(1)
    
    # Start CLI
    cli = ResearchAssistantCLI()
    cli.run()


if __name__ == "__main__":
    main()
