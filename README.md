# Multi-Agent Research Assistant

A production-grade, fault-tolerant autonomous research system built with LangGraph. 

Unlike standard single-prompt RAG applications, this system utilizes a cyclic, multi-agent architecture to execute complex research tasks. It features built-in self-reflection, automated retry loops for insufficient data, stateful conversational memory, and a Human-in-the-Loop (HITL) gatekeeper to prevent API token waste on ambiguous queries.

## Architecture: The 5-Agent Pipeline

The cognitive load is distributed across five specialized agents:

1. **Clarity Agent (The Gatekeeper):** Analyzes the user's prompt. If the query is vague or lacks context, it triggers an interrupt, pausing the graph to ask the user for clarification before proceeding.
2. **Research Agent:** Dynamically generates multiple targeted search queries and executes them in parallel. It scores its own confidence based on the quality of retrieved data.
3. **Validator Agent:** If the Research Agent's confidence is low, the Validator evaluates the findings against the original prompt, identifies exactly what is missing (e.g., "missing Q3 revenue"), and forces the Research Agent to retry with refined queries.
4. **Reflection Agent:** Critiques the finalized research payload for completeness, coherence, and contradictions before passing it to the writer.
5. **Synthesis Agent:** Drafts a comprehensive, multi-paragraph editorial report with grounded inline citations.

## Key Features
* **Stateful Orchestration:** Uses a SQLite Checkpointer to maintain multi-turn conversational memory (e.g., understanding that "their" refers to a previously researched company).
* **Resilient Fallbacks:** Gracefully catches LLM parsing errors with Pydantic retry prompts, and silently falls back to DuckDuckGo if the primary search API rate-limits.
* **Editorial UI:** Features a custom Alexandria-themed Streamlit interface for a clean, scholarly reading experience.
* **Free-Tier Optimized:** Engineered to run flawlessly on free-tier APIs (Groq + Tavily) without sacrificing production-quality latency.

---

## How to Run Locally

### 1. Prerequisites
Ensure you have **Python 3.11+** installed on your machine. You will also need free API keys from:
* [GroqCloud](https://console.groq.com/keys) (For the LLM)
* [Tavily](https://tavily.com/) (For the Search API)

### 2. Installation
Clone the repository and navigate into the project directory:
```bash
git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
cd YOUR-REPO-NAME
Create a virtual environment and activate it:

Bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
Install the required dependencies:

Bash
pip install -r requirements.txt
3. Environment Setup
Create a .env file in the root directory and add your API keys:

Code snippet
GROQ_API_KEY=gsk_your_groq_key_here
TAVILY_API_KEY=tvly_your_tavily_key_here
4. Launch the App
Run the Streamlit application:

Bash
streamlit run streamlit_app.py
The application will automatically open in your default web browser at http://localhost:8501.