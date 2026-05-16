import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Groq: For fast, short-context routing (Clarity, Research, Validator)
groq_llm = ChatGroq(
	model="llama-3.1-8b-instant",
	temperature=0,
	api_key=os.getenv("GROQ_API_KEY")
)

# Gemini: For heavy reading and report writing (Reflection, Synthesis)
gemini_llm = ChatGoogleGenerativeAI(
	model="gemini-3.1-flash-lite",
	temperature=0,
	api_key=os.getenv("GEMINI_API_KEY")
)

# Tavily API key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Maximum retry attempts for research validation loop
MAX_RETRY_ATTEMPTS = 3

# Confidence threshold for bypassing validation
CONFIDENCE_THRESHOLD = 6