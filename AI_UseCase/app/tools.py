import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain.tools import tool
from decouple import config
from app.config import get_config
from app.rag_pipeline import get_retriever
from db.database import create_or_get_customer, create_booking
from db.models import CustomerCreate, BookingCreate
from pydantic import BaseModel, ValidationError

app_config = get_config()

@tool("rag_search_tool")
def rag_search_tool(query: str) -> str:
    """Useful to find information from uploaded PDF documents about the business, services, pricing, terms, etc."""
    retriever = get_retriever()
    if not retriever:
        return "No documents have been uploaded or processed yet. Please ask the user to upload reference PDFs."
    
    docs = retriever.invoke(query)
    if not docs:
        return "Found no relevant information."
        
    return "\n\n".join([d.page_content for d in docs])

@tool("book_appointment_tool")
def book_appointment_tool(name: str, email: str, phone: str, booking_type: str, date: str, time: str) -> str:
    """
    Saves the confirmed booking to the database and sends a confirmation email.
    Use this ONLY after the user has explicitly confirmed all the details.
    Make sure date is in YYYY-MM-DD format and time is in HH:MM format.
    """
    try:
        # Create Customer
        customer = CustomerCreate(name=name, email=email, phone=phone)
        customer_id = create_or_get_customer(customer)
        
        # Create Booking
        booking = BookingCreate(
            customer_id=customer_id, 
            booking_type=booking_type,
            date=date,
            time=time
        )
        booking_id = create_booking(booking)
        
        # Trigger email silently (ignore failures but log them in return message if needed)
        email_status = "Email sent successfully."
        try:
            send_confirmation_email(name, email, booking_id, date, time, booking_type)
        except Exception as e:
            email_status = f"Email could not be sent, but booking was saved. Error: {str(e)}"
            
        return f"Booking successfully saved with ID {booking_id}. {email_status}"
        
    except ValidationError as e:
        return f"Validation Error in the inputs: {e}"
    except Exception as e:
        return f"An unexpected error occurred while saving to the database: {str(e)}"

def send_confirmation_email(recipient_name: str, recipient_email: str, booking_id: int, date: str, time: str, booking_type: str):
    """Internal helper to send confirmation emails via SMTP"""
    if not app_config.SENDER_EMAIL or not app_config.SENDER_PASSWORD:
        raise Exception("SMTP credentials are not configured in environment or secrets.")
        
    msg = MIMEMultipart()
    msg['From'] = app_config.SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = f"Booking Confirmation: #{booking_id}"
    
    body = f"""
    Hello {recipient_name},
    
    Your booking for {booking_type} has been confirmed.
    
    Booking Details:
    - ID: {booking_id}
    - Date: {date}
    - Time: {time}
    - Type: {booking_type}
    
    Thank you for booking with us!
    """
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(app_config.SMTP_SERVER, app_config.SMTP_PORT)
        server.starttls()
        server.login(app_config.SENDER_EMAIL, app_config.SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(app_config.SENDER_EMAIL, recipient_email, text)
        server.quit()
    except Exception as e:
        raise e

tools = [rag_search_tool, book_appointment_tool]
