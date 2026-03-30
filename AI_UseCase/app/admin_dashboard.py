import streamlit as st
import pandas as pd
from db.database import get_all_bookings

def render_admin_dashboard():
    st.title("🛡️ Admin Dashboard")
    st.markdown("View all bookings in the system below.")
    
    try:
        bookings = get_all_bookings()
    except Exception as e:
        st.error(f"Error reading database: {e}")
        return
        
    if not bookings:
        st.info("No bookings found in the database yet.")
        return
        
    # Convert to dataframe for nice Streamlit formatting
    df = pd.DataFrame(bookings)
    
    # Optional filters
    col1, col2 = st.columns(2)
    with col1:
        search_email = st.text_input("Filter by Email")
    with col2:
        search_date = st.text_input("Filter by Date (YYYY-MM-DD)")
        
    if search_email:
        df = df[df["email"].str.contains(search_email, case=False, na=False)]
    if search_date:
        df = df[df["date"].str.contains(search_date, case=False, na=False)]
        
    st.dataframe(
        df,
        column_config={
            "id": "Booking ID",
            "name": "Customer Name",
            "email": "Contact Email",
            "phone": "Phone", 
            "booking_type": "Service",
            "date": "Date",
            "time": "Time",
            "status": "Status",
            "created_at": "Submitted At"
        },
        hide_index=True,
        use_container_width=True
    )

    # Simple metric summaries
    st.subheader("Overview")
    col1, col2 = st.columns(2)
    col1.metric("Total Bookings", len(df))
    # E.g. Future bookings, etc could be calculated here
