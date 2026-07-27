import streamlit as st
from utils.helpers import get_doc_icon

def render_home_page():
    """Renders the Notebook Guide (Home page)."""
    
    # 1. EMPTY STATE: No documents uploaded yet
    if not st.session_state.documents:
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem 1.5rem; background-color: #111827; border: 1px solid #1e293b; border-radius: 16px; margin-top: 1rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🧠</div>
                <h2 style="font-size: 2.25rem; font-weight: 800; margin-bottom: 12px; font-family: 'Outfit';">
                    Welcome to your AI Notebook
                </h2>
                <p style="color: #94a3b8; font-size: 1.1rem; max-width: 600px; margin: 0 auto 2rem auto; line-height: 1.6;">
                    Create a personalized AI assistant. Upload your PDFs, text files, or documents, select them as sources, and instantly chat with them or generate summaries.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Big call to action button
        col_left, col_center, col_right = st.columns([4, 4, 4])
        with col_center:
            if st.button("📤 Add your first source", key="btn_home_upload", use_container_width=True, type="primary"):
                st.session_state.current_page = "Upload"
                st.rerun()
                
        # Onboarding Steps Grid
        st.markdown(
            """
            <div style="margin-top: 3rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px;">
                <div class="dm-card">
                    <div style="font-size: 1.75rem; margin-bottom: 12px; color: #3b82f6;">1. 📤 Upload Sources</div>
                    <h4 style="margin-bottom: 8px; font-family: 'Outfit';">Add your documents</h4>
                    <p style="color: #94a3b8; font-size: 0.9rem; margin: 0; line-height: 1.5;">Go to the <b>Add Source</b> page to upload files. Your backend can run OCR and extract text from PDFs, TXT, or images.</p>
                </div>
                <div class="dm-card">
                    <div style="font-size: 1.75rem; margin-bottom: 12px; color: #10b981;">2. 🎯 Select Context</div>
                    <h4 style="margin-bottom: 8px; font-family: 'Outfit';">Choose active files</h4>
                    <p style="color: #94a3b8; font-size: 0.9rem; margin: 0; line-height: 1.5;">Check the boxes next to your files in the left sidebar. The AI will only use the selected sources to answer questions.</p>
                </div>
                <div class="dm-card">
                    <div style="font-size: 1.75rem; margin-bottom: 12px; color: #8b5cf6;">3. 💬 Chat & Summarize</div>
                    <h4 style="margin-bottom: 8px; font-family: 'Outfit';">Interact with AI</h4>
                    <p style="color: #94a3b8; font-size: 0.9rem; margin: 0; line-height: 1.5;">Ask questions in the <b>Chat</b> tab, or head to <b>Summaries</b> to see syntheses of individual files or the whole notebook.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # 2. ACTIVE STATE: Documents uploaded
    total_sources = len(st.session_state.documents)
    selected_docs = [doc for doc in st.session_state.documents if doc["id"] in st.session_state.selected_doc_ids]
    selected_count = len(selected_docs)
    
    # Calculate total words across selected sources
    total_words = sum(doc.get("words", 0) for doc in selected_docs)

    # Metrics Row
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-value">{total_sources}</div>
                <div class="metric-label">Total Sources</div>
            </div>
            <div class="metric-box">
                <div class="metric-value" style="color: #10b981;">{selected_count}</div>
                <div class="metric-label">Selected Sources</div>
            </div>
            <div class="metric-box">
                <div class="metric-value" style="color: #8b5cf6;">{total_words:,}</div>
                <div class="metric-label">Total Words</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Workspace Layout
    col_left, col_right = st.columns([7, 5], gap="large")

    with col_left:
        st.markdown("<h3 style='margin-bottom: 16px; font-family: \"Outfit\";'>📖 Notebook Guide</h3>", unsafe_allow_html=True)
        
        # Notebook Guide Card
        st.markdown(
            """
            <div class="dm-card">
                <h4 style="margin-top: 0; margin-bottom: 12px; font-family: 'Outfit'; color: #3b82f6;">Getting Started</h4>
                <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; margin-bottom: 16px;">
                    This notebook contains your selected documents. You can interact with them as a collective brain. 
                    Use the navigation at the top to chat with them or read their summaries.
                </p>
                <div style="background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; font-size: 0.85rem; color: #94a3b8; line-height: 1.5;">
                    💡 <b>Tip:</b> You can select or deselect sources in the sidebar at any time to change the context of the AI's answers.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Quick Actions Grid
        st.markdown("<h4 style='margin-top: 20px; margin-bottom: 12px; font-family: \"Outfit\";'>Quick Actions</h4>", unsafe_allow_html=True)
        
        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            st.markdown(
                """
                <div style="background-color: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 16px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="font-size: 1.5rem; margin-bottom: 8px;">💬</div>
                        <h5 style="margin: 0 0 8px 0; font-size: 1rem; font-family: 'Outfit';">Chat Assistant</h5>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0 0 16px 0; line-height: 1.4;">Ask questions about your selected sources.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Open Chat", key="home_action_chat", use_container_width=True):
                st.session_state.current_page = "Chat"
                st.rerun()

        with col_act2:
            st.markdown(
                """
                <div style="background-color: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 16px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="font-size: 1.5rem; margin-bottom: 8px;">📝</div>
                        <h5 style="margin: 0 0 8px 0; font-size: 1rem; font-family: 'Outfit';">Read Summaries</h5>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0 0 16px 0; line-height: 1.4;">View summaries and key insights of your files.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Open Summaries", key="home_action_summary", use_container_width=True):
                st.session_state.current_page = "Summary"
                st.rerun()

    with col_right:
        st.markdown("<h3 style='margin-bottom: 16px; font-family: \"Outfit\";'>🎯 Selected Sources</h3>", unsafe_allow_html=True)
        
        if not selected_docs:
            st.markdown(
                """
                <div style="color: #64748b; font-size: 0.9rem; padding: 20px; background-color: #111827; border: 1px solid #1e293b; border-radius: 12px; text-align: center;">
                    No sources selected.<br>Please check one or more sources in the left sidebar to activate them.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for doc in selected_docs:
                icon = get_doc_icon(doc.get("type", "PDF"))
                st.markdown(
                    f"""
                    <div style="background-color: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 12px 16px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="font-size: 1.5rem;">{icon}</span>
                            <div>
                                <div style="font-weight: 600; font-size: 0.9rem; color: #ffffff; word-break: break-all;">{doc['name']}</div>
                                <div style="font-size: 0.75rem; color: #64748b;">{doc.get('size', '0 KB')} • {doc.get('pages', 1)} pages</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Developer hint box
            st.markdown(
                """
                <div style="margin-top: 24px; padding: 16px; background-color: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 12px;">
                    <h5 style="margin-top: 0; margin-bottom: 8px; font-family: 'Outfit'; color: #60a5fa; font-size: 0.9rem;">🛠️ Developer Note</h5>
                    <p style="margin: 0; font-size: 0.8rem; color: #94a3b8; line-height: 1.45;">
                        This frontend operates on <code>st.session_state.documents</code>. 
                        When you connect your backend, you can replace the empty OCR text and summaries with actual data returned from your server.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
