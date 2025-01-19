import streamlit as st
from modules.knowledge_graph import KnowledgeGraphRAG
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import tempfile

# Ensure this is the first Streamlit call
st.set_page_config(layout="wide", page_title="Knowledge Graph RAG System")

def render_app():
    st.title("🌟 Advanced RAG System with 3D Knowledge Graph")
    
    # Sidebar
    with st.sidebar:
        st.header("Controls")
        if st.button("🗑️ Delete Database"):
            st.session_state.rag.delete_database()
            st.success("Database cleared successfully!")

    # Main content
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        # Load and process the PDF
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        st.session_state.rag.create_vector_store(splits)
        st.session_state.rag.create_knowledge_graph(splits)

    question = st.text_input("Ask a question")
    if question:
        result = st.session_state.rag.query(question)
        st.write(result)
