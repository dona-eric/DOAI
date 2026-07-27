import time
import random
from typing import Generator, Dict, Any, List

def process_uploaded_file(file_name: str, file_size_bytes: int, file_content: bytes = None) -> Generator[Dict[str, Any], None, None]:
    """
    Handles the document processing pipeline.
    This function yields progress updates and finally returns the processed document metadata.
    
    TODO: Integrate your backend API here.
    Example:
        - Send `file_content` to your OCR and extraction backend.
        - Save the document into your database/vector store.
        - Return the actual OCR text, page count, word count, and summary.
    """
    steps = [
        ("Uploading file...", 0.25, 0.4),
        ("Extracting text (OCR)...", 0.50, 0.6),
        ("Generating summary...", 0.75, 0.5),
        ("Indexing in vector database...", 0.90, 0.4)
    ]
    
    for step_name, progress, duration in steps:
        yield {"step": step_name, "progress": progress, "status": "processing"}
        time.sleep(duration)
        
    # Format file size for display
    if file_size_bytes < 1024 * 1024:
        size_str = f"{file_size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{file_size_bytes / (1024 * 1024):.1f} MB"
        
    # Detect basic type from extension
    ext = file_name.split(".")[-1].upper() if "." in file_name else "DOC"
    
    # Create a clean document entry with empty fields for the backend to populate
    new_doc = {
        "id": f"doc_{int(time.time())}",
        "name": file_name,
        "size": size_str,
        "type": ext,
        "language": "Pending",  # To be detected by backend
        "pages": 1,             # To be calculated by backend
        "words": 0,             # To be calculated by backend
        "status": "Ready",
        "upload_time": "Just now",
        # Empty fields where backend data will go
        "ocr_text": "", 
        "summary": "",
        "chat_history": []
    }
    
    yield {
        "step": "Done",
        "progress": 1.0,
        "status": "completed",
        "document": new_doc
    }

def get_streaming_chat_response(selected_docs: List[Dict[str, Any]], chat_history: List[Dict[str, Any]], query: str) -> Generator[str, None, None]:
    """
    Streams the AI response based on the selected documents (sources) and the query.
    
    TODO: Connect your LLM backend here (e.g., LangChain, LlamaIndex, OpenAI, or Mistral).
    You will want to:
        1. Retrieve relevant chunks from your Vector DB using the `query` and filtering by `selected_docs` IDs.
        2. Pass the retrieved context + `chat_history` + `query` to your LLM.
        3. Stream the response back to the Streamlit UI.
    """
    # Create a helpful developer guidance message that acts as an interactive placeholder
    doc_names = [doc["name"] for doc in selected_docs]
    
    placeholder_response = (
        "🤖 **[Backend Connection Pending]**\n\n"
        "This is a frontend-only streaming placeholder. To chat with your documents, connect your LLM backend in `frontend/services/api.py`.\n\n"
        "**Context Sent to Backend:**\n"
        f"- **Active Sources ({len(doc_names)}):** {', '.join(doc_names) if doc_names else '*None selected*'}\n"
        f"- **User Query:** \"{query}\"\n"
        f"- **Chat History Length:** {len(chat_history)} messages\n\n"
        "Once you plug in your API call, the assistant will be able to answer questions directly using the text from these files."
    )
    
    # Stream the placeholder text to demonstrate the premium typing effect
    words = placeholder_response.split(" ")
    for word in words:
        yield word + " "
        time.sleep(0.02)  # Fast stream for responsive feel
