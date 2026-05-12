import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from utils.logger import get_logger

logger = get_logger("Memory")


def get_checkpointer():
    """
    Get checkpointer for conversation persistence.
    Prefers SQLite for production, falls back to in-memory.
    """
    try:
        # Create a direct SQLite connection
        db_path = "checkpoints.sqlite"
        conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # Initialize the saver with the connection
        memory = SqliteSaver(conn)
        
        # Ensure the database tables are created
        memory.setup()
        
        logger.info(f"[Memory] Using SQLite checkpointer: {db_path}")
        return memory
        
    except Exception as e:
        logger.warning(f"[Memory] SQLite failed: {str(e)}, using in-memory fallback")
        memory = MemorySaver()
        logger.info("[Memory] Using in-memory checkpointer")
        return memory