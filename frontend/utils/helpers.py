import streamlit as st
import os

def load_css():
    """Reads the custom CSS file and injects it into the Streamlit app."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback if CSS file is not found
        st.warning("CSS file not found at " + css_path)

def get_doc_icon(doc_type: str) -> str:
    """Returns an emoji icon based on the document type."""
    doc_type_lower = doc_type.lower()
    if "invoice" in doc_type_lower:
        return "🧾"
    elif "receipt" in doc_type_lower:
        return "🎫"
    elif "contract" in doc_type_lower or "agreement" in doc_type_lower:
        return "📜"
    elif "pdf" in doc_type_lower:
        return "📄"
    elif "image" in doc_type_lower or "png" in doc_type_lower or "jpg" in doc_type_lower:
        return "🖼️"
    return "📝"

def get_status_pill(status: str) -> str:
    """Returns HTML for a colored status pill."""
    status_lower = status.lower()
    if status_lower == "ready" or status_lower == "connected" or status_lower == "done":
        return f'<span class="status-pill online">● {status}</span>'
    elif status_lower == "processing" or status_lower == "loading":
        return f'<span class="status-pill warning">▲ {status}</span>'
    else:
        return f'<span class="status-pill offline">■ {status}</span>'
