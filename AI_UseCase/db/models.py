from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class CustomerCreate(BaseModel):
    name: str = Field(..., description="Full name of the customer")
    email: EmailStr = Field(..., description="Email address for confirmation")
    phone: str = Field(..., description="Contact phone number")

class BookingCreate(BaseModel):
    customer_id: Optional[int] = Field(default=None, description="Internal DB reference to customer")
    booking_type: str = Field(..., description="Type of consultation or service requested")
    date: str = Field(..., description="Date of booking in YYYY-MM-DD format")
    time: str = Field(..., description="Time of booking in HH:MM format")

class Customer(CustomerCreate):
    id: int

class Booking(BookingCreate):
    id: int
    status: str
    created_at: datetime
