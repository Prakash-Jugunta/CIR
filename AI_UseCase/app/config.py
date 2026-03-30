import os
from pydantic import BaseModel
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class AppConfig(BaseModel):
    # LLM Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = "llama3-8b-8192" # or llama3-70b-8192
    
    # Email Settings
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD", "")

    # Domain Specific
    BOOKING_DOMAIN: str = "Consultation/Service Booking"
    
def get_config() -> AppConfig:
    # First try fetching from streamlit secrets if available
    try:
        if "GROQ_API_KEY" in st.secrets:
            return AppConfig(
                GROQ_API_KEY=st.secrets["GROQ_API_KEY"],
                SENDER_EMAIL=st.secrets.get("SENDER_EMAIL", ""),
                SENDER_PASSWORD=st.secrets.get("SENDER_PASSWORD", "")
            )
    except FileNotFoundError:
        pass
        
    return AppConfig()
