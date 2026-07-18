import sqlite3
import pandas as pd
import os

DB_NAME = 'bookings.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service_type TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

def add_booking(name, phone, service_type, date, time):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO bookings (name, phone, service_type, date, time)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, phone, service_type, str(date), str(time)))
    booking_id = c.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def get_all_bookings():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM bookings", conn)
    conn.close()
    return df
