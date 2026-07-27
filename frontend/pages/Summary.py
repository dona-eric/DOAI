import streamlit as st
from utils.helpers import get_doc_icon

def render_summary_page():
    """Renders the document and notebook Summary page."""
    
    # Get currently selected sources
    selected_docs = [doc for doc in st.session_state.documents if doc["id"] in st.session_state.selected_doc_ids]
    
    st.markdown("<h3 style='margin-bottom: 16px; font-family: \"Outfit\";'>📝 Source Summaries</h3>", unsafe_allow_html=True)

    # 1. EMPTY STATE: No sources selected
    if not selected_docs:
        st.markdown(
            """
            <div style="padding: 2.5rem 1.5rem; background-color: #111827; border: 1px solid #1e293b; border-radius: 16px; text-align: center; margin-top: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📝</div>
                <h4 style="margin: 0 0 8px 0; font-family: 'Outfit'; color: #cbd5e1;">No Sources Selected</h4>
                <p style="color: #64748b; font-size: 0.95rem; max-width: 500px; margin: 0 auto;">
                    Please select one or more sources from the left sidebar to view their summaries and OCR text.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # 2. ACTIVE STATE: Display summaries in tabs
    tab_notebook, tab_individual = st.tabs(["🧬 Notebook Synthesis", "📄 Individual Sources"])

    # --- TAB 1: Notebook Synthesis ---
    with tab_notebook:
        st.markdown(
            """
            <div class="dm-card" style="margin-top: 15px;">
                <h4 style="margin-top: 0; margin-bottom: 12px; font-family: 'Outfit'; color: #3b82f6;">🧬 Combined Notebook Summary</h4>
                <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
                    <b>[Backend Connection Pending]</b>
                </p>
                <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.5;">
                    This section is designed to display a combined synthesis of all selected sources. 
                    When your backend is connected, you can send the OCR texts of all checked documents to your LLM and request a cross-document analysis.
                </p>
                <div style="background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 0.8rem; color: #60a5fa; margin-top: 15px;">
                    # Backend Integration Guideline:<br>
                    # Selected source IDs: {selected_ids}<br>
                    # Send prompt: "Summarize the key themes across these documents..."
                </div>
            </div>
            """.format(selected_ids=[doc["id"] for doc in selected_docs]),
            unsafe_allow_html=True
        )

    # --- TAB 2: Individual Sources ---
    with tab_individual:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        for doc in selected_docs:
            icon = get_doc_icon(doc.get("type", "PDF"))
            
            with st.expander(f"{icon} {doc['name']}", expanded=True):
                # Metadata Grid
                st.markdown(
                    f"""
                    <div class="metric-container" style="margin-top: 10px; margin-bottom: 15px;">
                        <div class="metric-box" style="padding: 10px;">
                            <div class="metric-value" style="font-size: 1.25rem;">{doc.get('type', 'Unknown')}</div>
                            <div class="metric-label" style="font-size: 0.65rem;">Type</div>
                        </div>
                        <div class="metric-box" style="padding: 10px;">
                            <div class="metric-value" style="font-size: 1.25rem;">{doc.get('size', '0 KB')}</div>
                            <div class="metric-label" style="font-size: 0.65rem;">Size</div>
                        </div>
                        <div class="metric-box" style="padding: 10px;">
                            <div class="metric-value" style="font-size: 1.25rem;">{doc.get('pages', 1)}</div>
                            <div class="metric-label" style="font-size: 0.65rem;">Pages</div>
                        </div>
                        <div class="metric-box" style="padding: 10px;">
                            <div class="metric-value" style="font-size: 1.25rem;">{doc.get('words', 0):,}</div>
                            <div class="metric-label" style="font-size: 0.65rem;">Words</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Layout for Summary and OCR text side-by-side or in nested tabs
                col_sum, col_ocr = st.columns(2, gap="medium")
                
                with col_sum:
                    st.markdown("<h5 style='margin-bottom: 8px; font-family: \"Outfit\"; color: #3b82f6;'>📝 Summary</h5>", unsafe_allow_html=True)
                    if doc.get("summary"):
                        st.markdown(
                            f"<div class='dm-card' style='padding: 15px !important; font-size: 0.9rem; min-height: 200px;'>{doc['summary']}</div>", 
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            """
                            <div style="border: 1px dashed #1e293b; border-radius: 12px; padding: 20px; text-align: center; color: #64748b; font-size: 0.85rem; min-height: 200px; display: flex; flex-direction: column; justify-content: center;">
                                📝 No summary generated yet.<br>
                                Connect your backend API to generate summaries when files are uploaded.
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                with col_ocr:
                    st.markdown("<h5 style='margin-bottom: 8px; font-family: \"Outfit\"; color: #60a5fa;'>📜 Extracted Text (OCR)</h5>", unsafe_allow_html=True)
                    if doc.get("ocr_text"):
                        st.markdown(
                            f"""
                            <div style="background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 15px; max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.8rem; color: #cbd5e1; white-space: pre-wrap;">{doc['ocr_text']}</div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            """
                            <div style="border: 1px dashed #1e293b; border-radius: 12px; padding: 20px; text-align: center; color: #64748b; font-size: 0.85rem; min-height: 200px; display: flex; flex-direction: column; justify-content: center;">
                                📜 OCR text is empty.<br>
                                Connect your OCR engine (e.g., Mistral OCR, Tesseract) to extract text.
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
