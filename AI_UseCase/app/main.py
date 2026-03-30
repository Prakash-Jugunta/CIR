import os
import sys
import tempfile
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.chat_logic import process_message
from app.admin_dashboard import render_admin_dashboard
from app.rag_pipeline import ingest_pdf
from db.database import init_db
from app.config import get_config

# DB Init at startup
init_db()
config = get_config()

st.set_page_config(
    page_title="AI Booking Assistant",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def chat_page():
    st.title(f"🤖 {config.BOOKING_DOMAIN} Assistant")
    st.markdown("I can answer questions about our services and help you book an appointment!")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Input
    if prompt := st.chat_input("Ask a question or request a booking..."):
        # Add user msg
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text = process_message(prompt, st.session_state.messages[:-1])
                st.markdown(response_text)
                
        # Append response
        st.session_state.messages.append({"role": "assistant", "content": response_text})

def main():
    css = """
    <style>
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 5px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to", ["Chat Interface", "Admin Dashboard"])
        st.divider()
        
        if page == "Chat Interface":
            st.subheader("📚 Knowledge Base")
            uploaded_files = st.file_uploader(
                "Upload reference PDFs for QA", 
                type=["pdf"], 
                accept_multiple_files=True
            )
            
            if st.button("Process Documents"):
                if uploaded_files:
                    with st.spinner("Ingesting PDFs..."):
                        total_chunks = 0
                        for file in uploaded_files:
                            # Save temporarily to disk for PyMuPDF
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tf:
                                tf.write(file.getbuffer())
                                tf_path = tf.name
                                
                            try:
                                chunks = ingest_pdf(tf_path)
                                total_chunks += chunks
                            except Exception as e:
                                st.error(f"Error processing {file.name}: {e}")
                            finally:
                                os.unlink(tf_path)
                        st.success(f"Successfully processed {len(uploaded_files)} PDF(s) into {total_chunks} chunk(s)!")
                else:
                    st.warning("Please upload at least one PDF.")
                    
            st.divider()
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                st.rerun()

    if page == "Chat Interface":
        chat_page()
    else:
        render_admin_dashboard()

if __name__ == "__main__":
    if not config.GROQ_API_KEY:
        st.error("Error: A valid GROQ_API_KEY environment variable or Streamlit Secret is required.")
    else:
        main()
