import streamlit as st
from utils.helpers import get_doc_icon

def render_sidebar():
    """Renders the NotebookLM-style Sources sidebar."""
    with st.sidebar:
        # Title & Brand
        st.markdown(
            """
            <div style="padding: 10px 0; text-align: center; margin-bottom: 20px; border-bottom: 1px solid #1e293b;">
                <h2 style="margin: 0; font-size: 1.5rem; letter-spacing: -0.025em; display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <span style="background: linear-gradient(to right, #3b82f6, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">DocMind AI</span>
                </h2>
                <div style="color: #64748b; font-size: 0.75rem; margin-top: 4px;">NotebookLM Workspace</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 1. Add Source Button
        if st.button("➕ Add Source", key="sidebar_add_source", use_container_width=True, type="primary"):
            st.session_state.current_page = "Upload"
            st.rerun()

        st.markdown("<div style='margin: 20px 0; border-top: 1px solid #1e293b;'></div>", unsafe_allow_html=True)

        # 2. Sources Header & Selection Utilities
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">📁 Sources</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not st.session_state.documents:
            st.markdown(
                """
                <div style="color: #475569; font-size: 0.85rem; padding: 15px; border: 1px dashed #1e293b; border-radius: 8px; text-align: center;">
                    No sources added yet.<br>Click <b>Add Source</b> to upload.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Select All / Clear Selection Buttons
            col_sel, col_clr = st.columns(2)
            if col_sel.button("Select All", key="btn_select_all", use_container_width=True):
                st.session_state.selected_doc_ids = [doc["id"] for doc in st.session_state.documents]
                st.rerun()
            if col_clr.button("Clear All", key="btn_clear_all", use_container_width=True):
                st.session_state.selected_doc_ids = []
                st.rerun()

            st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

            # List of sources with checkboxes
            for idx, doc in enumerate(st.session_state.documents):
                doc_id = doc["id"]
                doc_name = doc["name"]
                doc_type = doc.get("type", "PDF")
                
                # Truncate long names for sidebar
                display_name = doc_name
                if len(display_name) > 18:
                    display_name = display_name[:15] + "..."

                # We use columns to align Checkbox and a Delete button
                col_check, col_del = st.columns([8, 2])
                
                with col_check:
                    # Checkbox for selecting document into the active context
                    is_selected = doc_id in st.session_state.selected_doc_ids
                    icon = get_doc_icon(doc_type)
                    
                    checked = st.checkbox(
                        label=f"{icon} {display_name}",
                        value=is_selected,
                        key=f"check_{doc_id}_{idx}"
                    )
                    
                    # Update selected list based on checkbox state
                    if checked and doc_id not in st.session_state.selected_doc_ids:
                        st.session_state.selected_doc_ids.append(doc_id)
                        st.rerun()
                    elif not checked and doc_id in st.session_state.selected_doc_ids:
                        st.session_state.selected_doc_ids.remove(doc_id)
                        st.rerun()
                
                with col_del:
                    # Delete button
                    if st.button("🗑️", key=f"del_{doc_id}_{idx}", help=f"Remove {doc_name}"):
                        # Remove from documents list
                        st.session_state.documents = [d for d in st.session_state.documents if d["id"] != doc_id]
                        # Remove from selected list if present
                        if doc_id in st.session_state.selected_doc_ids:
                            st.session_state.selected_doc_ids.remove(doc_id)
                        # Clear processed session key if it exists
                        file_key = f"processed_{doc_name}_{doc.get('size_bytes', 0)}"
                        if file_key in st.session_state:
                            del st.session_state[file_key]
                        st.rerun()

        # Sticky bottom status card showing active selection
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        
        selected_count = len(st.session_state.selected_doc_ids)
        total_count = len(st.session_state.documents)
        
        st.markdown(
            f"""
            <div style="background-color: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 14px; margin-top: auto;">
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                    🎯 Active Context
                </div>
                <div style="font-size: 0.85rem; color: #cbd5e1; display: flex; justify-content: space-between;">
                    <span>Selected Sources:</span>
                    <span style="font-weight: 700; color: #3b82f6;">{selected_count} / {total_count}</span>
                </div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px; line-height: 1.3;">
                    Only checked sources will be used by the AI to answer questions and generate summaries.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
