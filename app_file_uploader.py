"""
based on Streamlit, build a simple web page to upload files and store them in the vector database
"""
import time
from knowledge_base import Knowledge_base
import streamlit as st


# add webpage title
st.title("knowledge base update service")

# file_uploader
uploaded_file = st.file_uploader(
    "please upload a TXT file",
    type=['txt'],
    accept_multiple_files=False,    # False means only accept one file upload
)

# session_state is a dictionary
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if uploaded_file is not None:
    # extract file information
    file_name = uploaded_file.name
    file_type = uploaded_file.type
    file_size = uploaded_file.size / 1024   # KB

    st.subheader(f"file name: {file_name}")
    st.write(f"format: {file_type} | size: {file_size:.2f} KB")

    # get_value -> bytes -> decode('utf-8')
    content = uploaded_file.getvalue().decode("utf-8")

    with st.spinner("loading into knowledge base..."):       # during the execution of the code in spinner, there will be a spinning animation
        time.sleep(1)
        result = st.session_state["service"].upload_by_str(content, file_name)
        st.write(result)