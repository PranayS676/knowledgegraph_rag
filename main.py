from modules.ui import render_app
from modules.knowledge_graph import KnowledgeGraphRAG
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GROQ_API_KEY

if __name__ == "__main__":
    import streamlit as st
    if "rag" not in st.session_state:
        st.session_state.rag = KnowledgeGraphRAG(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GROQ_API_KEY)
    render_app()