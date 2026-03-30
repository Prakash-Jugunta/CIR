import sqlite3
import os
from datetime import datetime
from db.models import CustomerCreate, BookingCreate

DB_PATH = os.path.join(os.path.dirname(__file__), 'bookings.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL
    )
    ''')
    
    # Create bookings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        booking_type TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT DEFAULT 'CONFIRMED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def create_or_get_customer(customer_data: CustomerCreate) -> int:
    """Returns customer_id from DB"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT id FROM customers WHERE email = ?", (customer_data.email,))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return existing[0]
        
    cursor.execute(
        "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
        (customer_data.name, customer_data.email, customer_data.phone)
    )
    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()
    
    return customer_id

def create_booking(booking_data: BookingCreate) -> int:
    """Returns booking_id"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO bookings (customer_id, booking_type, date, time) VALUES (?, ?, ?, ?)",
        (booking_data.customer_id, booking_data.booking_type, booking_data.date, booking_data.time)
    )
    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()
    
    return booking_id

def get_all_bookings():
    """Retrieve all bookings for the Admin Dashboard"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Join bookings and customers
    cursor.execute('''
    SELECT 
        b.id, c.name, c.email, c.phone, b.booking_type, b.date, b.time, b.status, b.created_at
    FROM bookings b
    JOIN customers c ON b.customer_id = c.id
    ORDER BY b.date DESC, b.time DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
