import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Groq configuration with temperature=0 for deterministic outputs
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# Tavily API key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Maximum retry attempts for research validation loop
MAX_RETRY_ATTEMPTS = 3

# Confidence threshold for bypassing validation
CONFIDENCE_THRESHOLD = 6
