import streamlit as st


#=============CONFIGURATION ===================

st.page_config(
    page_title="DocMind AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


#=============SIDEBAR ===================

with st.sidebar:
    st.selectbox('Select the files', ["PDF", "DOCX", "PPTX","Images", "TXT"])
    st.file_uploader("Upload")





if __name__ == "__main__":
    main()