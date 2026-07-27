import streamlit as st
from utils.helpers import load_css
from components.sidebar import render_sidebar
from pages.Home import render_home_page
from pages.Chat import render_chat_page
from pages.Summary import render_summary_page
from pages.Upload import render_upload_page

# 1. Page Configuration
st.set_page_config(
    page_title="DocMind AI - NotebookLM Workspace",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Session State Initialization
if "documents" not in st.session_state:
    st.session_state.documents = []  # Empty by default (no mock data)

if "selected_doc_ids" not in st.session_state:
    st.session_state.selected_doc_ids = []  # No documents selected initially

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

if "global_chat_history" not in st.session_state:
    st.session_state.global_chat_history = []  # Chat history across selected sources

# 3. Load & Inject Custom CSS Styles
load_css()

# 4. Render Sidebar (Left Column: Sources Panel)
render_sidebar()

# 5. Main Area Top Header & Navigation
# We display the notebook name and a clean tab-based navigation bar
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; margin-bottom: 20px; border-bottom: 1px solid #1e293b;">
        <div>
            <h1 style="margin: 0; font-size: 1.75rem; font-family: 'Outfit'; font-weight: 700; background: linear-gradient(to right, #3b82f6, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                📓 Document Notebook
            </h1>
            <div style="color: #64748b; font-size: 0.85rem; margin-top: 2px;">NotebookLM-inspired AI Workspace</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Horizontal Navigation Bar using Columns
nav_cols = st.columns([3, 3, 3, 3, 4])  # Adjusted column widths to prevent truncation

pages_config = [
    ("Home", "🏠 Guide"),
    ("Chat", "💬 Chat"),
    ("Summary", "📝 Summaries"),
    ("Upload", "📤 Upload")
]

for idx, (page_id, page_label) in enumerate(pages_config):
    is_active = st.session_state.current_page == page_id
    button_label = f"👉 {page_label}" if is_active else page_label
    
    if nav_cols[idx].button(
        button_label, 
        key=f"nav_top_{page_id}", 
        use_container_width=True,
        type="primary" if is_active else "secondary"
    ):
        st.session_state.current_page = page_id
        st.rerun()

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# 6. Page Routing (Center Area)
if st.session_state.current_page == "Home":
    render_home_page()
elif st.session_state.current_page == "Chat":
    render_chat_page()
elif st.session_state.current_page == "Summary":
    render_summary_page()
elif st.session_state.current_page == "Upload":
    render_upload_page()
