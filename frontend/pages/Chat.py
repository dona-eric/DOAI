import streamlit as st
from services.api import get_streaming_chat_response
from utils.helpers import get_doc_icon

def render_chat_page():
    """Renders the conversational Chat page."""
    
    # Get currently selected sources
    selected_docs = [doc for doc in st.session_state.documents if doc["id"] in st.session_state.selected_doc_ids]
    
    # Header with a Clear Chat button
    col_title, col_clear = st.columns([8, 2])
    with col_title:
        st.markdown("<h3 style='margin: 0; font-family: \"Outfit\";'>💬 Chat Assistant</h3>", unsafe_allow_html=True)
    with col_clear:
        if st.button("🗑️ Clear Chat", key="btn_clear_chat", use_container_width=True):
            st.session_state.global_chat_history = []
            st.toast("Chat history cleared!")
            st.rerun()

    # Active Context Pills Bar
    if selected_docs:
        pills_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 20px 0; align-items: center;'>"
        pills_html += "<span style='color: #94a3b8; font-size: 0.85rem; font-weight: 500;'>Chatting with:</span>"
        for doc in selected_docs:
            icon = get_doc_icon(doc.get("type", "PDF"))
            pills_html += f"""
            <span style='background-color: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; color: #60a5fa; display: flex; align-items: center; gap: 6px;'>
                {icon} {doc['name']}
            </span>
            """
        pills_html += "</div>"
        st.markdown(pills_html, unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div style="margin: 12px 0 20px 0; padding: 16px; background-color: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 12px; color: #f87171; font-size: 0.9rem;">
                ⚠️ <b>No sources selected.</b> Please check at least one source in the left sidebar to start chatting.
            </div>
            """,
            unsafe_allow_html=True
        )

    # Chat History Container
    if not st.session_state.global_chat_history:
        # Initial greeting
        st.markdown(
            """
            <div style="text-align: center; color: #64748b; padding: 4rem 1rem;">
                <div style="font-size: 3rem; margin-bottom: 12px;">💬</div>
                <h4 style="margin: 0 0 8px 0; font-family: 'Outfit'; color: #cbd5e1;">Start a Conversation</h4>
                <p style="margin: 0; font-size: 0.9rem;">Ask a question about the selected sources. The AI will answer based on their content.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Render message history
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.global_chat_history:
            role = msg["role"]
            content = msg["content"]
            avatar_label = "U" if role == "user" else "AI"
            bubble_class = "user" if role == "user" else "assistant"
            
            # Simple formatting for HTML display
            formatted_content = content.replace("**", "<b>").replace("**", "</b>")
            formatted_content = formatted_content.replace("\n", "<br>")
            
            chat_html += f"""
            <div class="chat-bubble {bubble_class}">
                <div class="chat-avatar {bubble_class}">{avatar_label}</div>
                <div style="padding-top: 4px; flex-grow: 1;">{formatted_content}</div>
            </div>
            """
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

    # Chat Input (Disabled if no sources are selected)
    input_placeholder = "Ask anything about your sources..." if selected_docs else "Select a source in the sidebar to enable chat..."
    user_input = st.chat_input(input_placeholder, disabled=not selected_docs)
    
    if user_input:
        # Append user message
        st.session_state.global_chat_history.append({"role": "user", "content": user_input})
        st.rerun()

    # Handle AI response generation
    if st.session_state.global_chat_history and st.session_state.global_chat_history[-1]["role"] == "user":
        # Render a temporary streaming bubble
        st.markdown(
            """
            <div class="chat-bubble assistant" style="margin-top: 10px;">
                <div class="chat-avatar assistant">AI</div>
                <div style="padding-top: 4px; flex-grow: 1;" id="streaming-text">
            """,
            unsafe_allow_html=True
        )
        
        text_placeholder = st.empty()
        full_response = ""
        
        # Call streaming API from services.api
        # Pass the selected sources, the previous history, and the last query
        history_to_send = st.session_state.global_chat_history[:-1]
        query_to_send = st.session_state.global_chat_history[-1]["content"]
        
        for chunk in get_streaming_chat_response(selected_docs, history_to_send, query_to_send):
            full_response += chunk
            text_placeholder.markdown(f"{full_response}▌")
            
        # Clear the temporary placeholder and close HTML tags
        text_placeholder.empty()
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Append the finished response to history and rerun
        st.session_state.global_chat_history.append({"role": "assistant", "content": full_response})
        st.rerun()
