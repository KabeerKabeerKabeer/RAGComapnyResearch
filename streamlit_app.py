import streamlit as st
import uuid
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from graph import get_graph

# Load environment variables
load_dotenv()

# --- PAGE CONFIGURATION ---
# Collapse sidebar by default to maintain the blank canvas look
st.set_page_config(
	page_title="Business Intelligence",
	page_icon="🌌",
	layout="centered",
	initial_sidebar_state="collapsed"
)

# --- GLASSMORPHISM CSS INJECTION ---
GLASS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');

/* Hide native Streamlit UI elements (header, footer, sidebar toggle) */
header {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="collapsedControl"] {display: none !important;}
[data-testid="stSidebar"] {display: none !important;}

/* Full Page Background Gradient (Blue-Black) */
.stApp {
	background: linear-gradient(135deg, #020617 0%, #0f172a 100%) !important;
	background-attachment: fixed !important;
}

/* Global Typography */
html, body, p, li, h1, h2, h3, h4, h5, h6 {
	font-family: 'Inter', sans-serif !important;
}

/* Force text color to white, but DO NOT overwrite the icon font-families */
.stApp * {
	color: #F8FAFC !important; 
}

/* Adjust main container to remove top padding */
.block-container {
	padding-top: 2rem !important;
	max-width: 900px !important;
}

/* --- THE FLOATING CHAT INPUT --- */
div[data-testid="stChatInput"] {
	background: rgba(30, 41, 59, 0.4) !important;
	backdrop-filter: blur(16px) !important;
	-webkit-backdrop-filter: blur(16px) !important;
	border: 1px solid rgba(255, 255, 255, 0.1) !important;
	border-radius: 24px !important;
	box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
	padding: 5px !important;
	margin-bottom: 20px !important;
}

div[data-testid="stChatInput"] textarea {
	color: #FFFFFF !important;
}

/* --- MESSAGE BUBBLES --- */
/* Remove default backgrounds and shadows */
div[data-testid="stChatMessage"] {
	background-color: transparent !important;
	border: none !important;
	box-shadow: none !important;
	padding: 1.5rem !important;
}

/* User Message (Right-aligned feel, glass pill) */
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
	background: rgba(255, 255, 255, 0.05) !important;
	backdrop-filter: blur(10px) !important;
	-webkit-backdrop-filter: blur(10px) !important;
	border: 1px solid rgba(255, 255, 255, 0.05) !important;
	border-radius: 16px !important;
	margin: 1rem 0 1rem auto !important;
	width: fit-content !important;
	max-width: 80% !important;
}

/* AI Message (Left-aligned, transparent blending) */
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
	background: transparent !important;
	border-left: 2px solid rgba(255, 255, 255, 0.1) !important;
	border-radius: 0 !important;
	margin: 1rem auto 1rem 0 !important;
}

/* Hide avatars to make it just floating text */
div[data-testid="chatAvatarIcon-user"], div[data-testid="chatAvatarIcon-assistant"] {
	display: none !important;
}

/* Status Widget (Glassy) */
div[data-testid="stStatusWidget"] {
	background: rgba(30, 41, 59, 0.4) !important;
	backdrop-filter: blur(10px) !important;
	border: 1px solid rgba(255, 255, 255, 0.1) !important;
	border-radius: 12px !important;
}
</style>
"""
st.markdown(GLASS_CSS, unsafe_allow_html=True)


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

# --- MAIN CHAT INTERFACE ---
# --- MAIN CHAT INTERFACE ---
# Display chat history
for msg in st.session_state.messages:
	# Assign the correct emoji based on who is speaking
	avatar_icon = "👤" if msg["role"] == "user" else "🤖"
	
	with st.chat_message(msg["role"], avatar=avatar_icon):
		st.markdown(msg["content"])

# --- CHAT INPUT & LOGIC ---
if prompt := st.chat_input("Ask a Business inquiry"):
	
	st.session_state.messages.append({"role": "user", "content": prompt})
	
	# Force the user emoji here
	with st.chat_message("user", avatar="👤"):
		st.markdown(prompt)

	# Force the AI emoji here
	with st.chat_message("assistant", avatar="🤖"):
		with st.status("Processing...", expanded=True) as status_container:
			try:
				if st.session_state.awaiting_clarification:
					st.write("Resuming analysis...")
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
				
				for event in graph.stream(state_input, config):
					for node_name, node_state in event.items():
						if node_name == "clarity_agent":
							st.write("Parsing intent...")
						elif node_name == "research_agent":
							st.write("Executing data retrieval...")
						elif node_name == "validator_agent":
							st.write("Validating findings...")
						elif node_name == "reflection_agent":
							st.write("Synthesizing context...")
						elif node_name == "synthesis_agent":
							st.write("Formatting response...")
							final_response = node_state.get("final_response")

				current_state = graph.get_state(config)
				if current_state.values.get("clarity_status") == "needs_clarification":
					clarification_q = current_state.values.get("clarification_question")
					st.session_state.awaiting_clarification = True
					
					status_container.update(label="Clarification Required", state="complete", expanded=False)
					st.markdown(f"**{clarification_q}**")
					st.session_state.messages.append({"role": "assistant", "content": f"**{clarification_q}**"})

				elif final_response:
					status_container.update(label="Complete", state="complete", expanded=False)
					st.markdown(final_response)
					st.session_state.messages.append({"role": "assistant", "content": final_response})

			except Exception as e:
				status_container.update(label="System Exception", state="error", expanded=False)
				st.error(f"Error: {str(e)}")