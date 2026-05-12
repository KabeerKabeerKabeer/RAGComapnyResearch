import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific component."""
    return logging.getLogger(name)


# Create agent-specific loggers
clarity_logger = get_logger("ClarityAgent")
research_logger = get_logger("ResearchAgent")
validator_logger = get_logger("ValidatorAgent")
reflection_logger = get_logger("ReflectionAgent")
synthesis_logger = get_logger("SynthesisAgent")
graph_logger = get_logger("GraphOrchestrator")
search_logger = get_logger("SearchTools")
