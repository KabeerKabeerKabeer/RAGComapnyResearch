import streamlit as st
import uuid
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from graph import get_graph

# Load environment variables
load_dotenv()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Kabeer ALi- SynapseAi Assignment",
    page_icon="🏛️",
    layout="centered" # Using centered natively, but CSS overrides max-width to 1200px
)

# --- ALEXANDRIA THEME CSS INJECTION ---
ALEXANDRIA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Serif:ital,wght@0,400;0,700;1,400&display=swap');

/* Main Container Width Override */
.block-container {
    max-width: 1200px !important;
    padding-top: 2rem !important;
}

/* Typography Overrides */
html, body, p, li, h1, h2, h3, h4, h5, h6 {
    font-family: 'Noto Serif', serif !important;
    color: #1A1A1A !important;
}

/* Utility elements use Sans-Serif (Inter) */
button, input, .stChatInput textarea, .stSidebar p {
    font-family: 'Inter', sans-serif !important;
}

/* Remove elevations and shadows universally */
div[data-testid="stChatMessage"], div[data-testid="stChatInput"] {
    box-shadow: none !important;
}

/* AI Message Styling (Left Aligned, Flat, White) */
div[data-testid="chatAvatarIcon-assistant"] {
    background-color: #3366cc !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background-color: #FFFFFF !important;
    border-radius: 4px !important;
    padding: 1.5rem 0 !important;
    border-top: 1px solid #F8F9FA;
    border-bottom: 1px solid #F8F9FA;
}

/* User Message Styling (Subtle container, right-aligned feeling via background) */
div[data-testid="chatAvatarIcon-user"] {
    background-color: #1A1A1A !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background-color: #F8F9FA !important;
    border-radius: 4px !important;
    padding: 1.5rem !important;
    margin: 1rem 0 !important;
}

/* Chat Input Bar (Bottom anchored, pill-shaped) */
div[data-testid="stChatInput"] {
    border-radius: 4px !important;
    border: 1px solid #E0E0E0 !important;
    background-color: #FFFFFF !important;
}

/* Source Pill Tags */
.source-pill {
    display: inline-block;
    background-color: #F8F9FA;
    color: #4A4A4A;
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    padding: 4px 12px;
    border-radius: 16px;
    margin-right: 8px;
    margin-bottom: 8px;
    border: 1px solid #EBEBEB;
    text-decoration: none;
}
.source-pill:hover {
    background-color: #3366cc;
    color: #FFFFFF;
    border-color: #3366cc;
}

/* Status Dropdown (Agents working) */
div[data-testid="stStatusWidget"] {
    border-radius: 4px !important;
    border: 1px solid #F8F9FA !important;
    background-color: #FFFFFF !important;
}
</style>
"""
st.markdown(ALEXANDRIA_CSS, unsafe_allow_html=True)


# --- INITIALIZATION ---
@st.cache_resource
def load_graph():
    return get_graph()

graph = load_graph()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "awaiting_clarification" not in st.session_state:
    st.session_state.awaiting_clarification = False

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='font-family: Noto Serif;'>Kabeer Ali - SynapseAI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4A4A4A; font-family: Inter; font-size: 0.9rem;'>Digital Curator & Research Intelligence</p>", unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("New Session", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.awaiting_clarification = False
        st.rerun()

# --- MAIN CHAT INTERFACE ---
if not st.session_state.messages:
    st.markdown("<h1 style='text-align: center; color: #1A1A1A; margin-top: 4rem;'>Research Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4A4A4A; max-width: 600px; margin: 0 auto; font-family: Inter;'>Enter a company name or entity to generate a comprehensive, scholarly report.</p>", unsafe_allow_html=True)

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT & LOGIC ---
if prompt := st.chat_input("E.g., Detail the recent financial filings of NVIDIA..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Curating sources...", expanded=True) as status_container:
            try:
                if st.session_state.awaiting_clarification:
                    st.write("🔄 *Resuming analysis...*")
                    current_state = graph.get_state(config)
                    
                    state_input = {
                        **current_state.values,
                        "clarified_query": prompt,
                        "company_name": prompt,
                        "clarity_status": "clear",
                        "messages": [HumanMessage(content=prompt)]
                    }
                    st.session_state.awaiting_clarification = False
                    
                else:
                    state_input = {
                        "messages": [HumanMessage(content=prompt)],
                        "user_query": prompt,
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

                final_response = None
                sources_data = None
                
                for event in graph.stream(state_input, config):
                    for node_name, node_state in event.items():
                        if node_name == "clarity_agent":
                            st.write("🕵️‍♂️ **Parsing query syntax...**")
                        elif node_name == "research_agent":
                            attempt = node_state.get("attempts", 1)
                            st.write(f"🔍 **Acquiring documents (Cycle {attempt})...**")
                            # Capture sources to format them as pills later
                            sources_data = node_state.get("sources", [])
                        elif node_name == "validator_agent":
                            val = node_state.get("validation_result")
                            st.write(f"⚖️ **Evaluating data sufficiency ({val})...**")
                        elif node_name == "reflection_agent":
                            st.write("💭 **Cross-referencing findings...**")
                        elif node_name == "synthesis_agent":
                            st.write("✍️ **Drafting editorial report...**")
                            final_response = node_state.get("final_response")

                current_state = graph.get_state(config)
                if current_state.values.get("clarity_status") == "needs_clarification":
                    clarification_q = current_state.values.get("clarification_question")
                    st.session_state.awaiting_clarification = True
                    
                    status_container.update(label="Clarification Required", state="complete", expanded=False)
                    st.markdown(f"**{clarification_q}**")
                    st.session_state.messages.append({"role": "assistant", "content": f"**{clarification_q}**"})

                elif final_response:
                    status_container.update(label="Report Compiled", state="complete", expanded=False)
                    
                    # Optional: Automatically format markdown links at the bottom as "Source Pills"
                    # If the LLM outputs standard markdown lists at the bottom, this renders them normally.
                    # To strictly enforce the pill UI, the prompt needs to output HTML, but standard markdown looks clean in Serif.
                    
                    st.markdown(final_response)
                    st.session_state.messages.append({"role": "assistant", "content": final_response})

            except Exception as e:
                status_container.update(label="System Exception", state="error", expanded=False)
                st.error(f"Error: {str(e)}")