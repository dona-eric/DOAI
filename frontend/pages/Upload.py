import streamlit as st
import time
from services.api import process_uploaded_file
from utils.helpers import get_doc_icon

def render_upload_page():
    """Renders the file upload page (Add Source)."""
    
    st.markdown("<h3 style='margin-bottom: 16px; font-family: \"Outfit\";'>📤 Add Source</h3>", unsafe_allow_html=True)
    
    col_upload, col_recent = st.columns([7, 5], gap="large")
    
    with col_upload:
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <h4 style="margin: 0 0 8px 0; font-family: 'Outfit';">Upload Files</h4>
                <p style="color: #94a3b8; font-size: 0.9rem; margin: 0; line-height: 1.5;">
                    Upload documents to add them to your notebook. The AI will index them for semantic search and Q&A.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # File Uploader
        uploaded_file = st.file_uploader(
            "Upload files",
            type=["pdf", "txt", "md", "docx", "csv", "json"],
            label_visibility="collapsed",
            key="notebook_file_uploader"
        )
        
        # Process Uploaded File
        if uploaded_file is not None:
            # Prevent duplicate processing on page reruns
            file_key = f"processed_{uploaded_file.name}_{uploaded_file.size}"
            if file_key not in st.session_state:
                st.markdown("<div class='dm-card' style='margin-top: 20px;'>", unsafe_allow_html=True)
                
                status_container = st.empty()
                progress_bar = st.progress(0)
                
                # Run backend processing simulation
                # Reading file binary data if needed
                file_bytes = uploaded_file.getvalue()
                
                for update in process_uploaded_file(uploaded_file.name, uploaded_file.size, file_bytes):
                    status_container.markdown(
                        f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-weight: 600; color: #3b82f6;">{update['step']}</span>
                            <span style="font-size: 0.85rem; color: #94a3b8;">{int(update['progress'] * 100)}%</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    progress_bar.progress(update["progress"])
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Extract processed document data from the final yield
                if "document" in update:
                    new_doc = update["document"]
                    
                    # Append to session state documents
                    st.session_state.documents.append(new_doc)
                    # Automatically select the newly uploaded source (NotebookLM behavior)
                    if new_doc["id"] not in st.session_state.selected_doc_ids:
                        st.session_state.selected_doc_ids.append(new_doc["id"])
                    
                    st.session_state[file_key] = True
                    
                    # Show success toast
                    st.toast(f"🎉 {uploaded_file.name} successfully added!", icon="✅")
                    time.sleep(1.0)
                    st.rerun()

        # Instructions/Information
        st.markdown(
            """
            <div style="margin-top: 2rem;">
                <h5 style="margin-bottom: 10px; font-family: 'Outfit';">Supported Formats</h5>
                <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                    <span style="background-color: #1e293b; border: 1px solid #334155; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; color: #cbd5e1;">📄 PDF</span>
                    <span style="background-color: #1e293b; border: 1px solid #334155; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; color: #cbd5e1;">📝 TXT / MD</span>
                    <span style="background-color: #1e293b; border: 1px solid #334155; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; color: #cbd5e1;">📊 CSV / JSON</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_recent:
        st.markdown(
            """
            <h4 style="margin: 0 0 16px 0; font-family: 'Outfit';">Recently Uploaded</h4>
            """,
            unsafe_allow_html=True
        )
        
        if not st.session_state.documents:
            st.markdown(
                """
                <div style="color: #64748b; font-size: 0.9rem; padding: 20px; background-color: #111827; border: 1px solid #1e293b; border-radius: 12px; text-align: center;">
                    No sources uploaded in this session.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Display all uploaded documents, starting from the most recent
            for doc in reversed(st.session_state.documents):
                icon = get_doc_icon(doc.get("type", "PDF"))
                is_selected = doc["id"] in st.session_state.selected_doc_ids
                status_color = "#10b981" if is_selected else "#64748b"
                status_text = "Active Context" if is_selected else "Inactive"
                
                st.markdown(
                    f"""
                    <div style="background-color: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 12px 16px; margin-bottom: 10px;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 1.25rem;">{icon}</span>
                                <span style="font-weight: 600; font-size: 0.85rem; color: #ffffff; word-break: break-all;">{doc['name']}</span>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748b;">
                            <span>{doc.get('size', '0 KB')} • {doc.get('pages', 1)} pages</span>
                            <span style="color: {status_color}; font-weight: 600;">{status_text}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
