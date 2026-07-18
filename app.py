import streamlit as st
import database as db
import urllib.parse
import datetime
import re

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Pinky Healthcare Booking",
    page_icon="⚕️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- CSS STYLING ---
# Theme tailored for Pinky Healthcare
st.markdown("""
    <style>
    .main {
        background-color: #fcfcfc;
        color: #1f2937;
    }
    h1 {
        color: #be185d; /* Pinky accent color */
        font-family: 'Inter', sans-serif;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center; 
        color: #4b5563; 
        font-size: 1.15rem; 
        margin-bottom: 2.5rem;
    }
    .stButton>button {
        background-color: #25D366; /* WhatsApp Green */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #128C7E;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        color: white;
    }
    .booking-success {
        padding: 1.5rem;
        background-color: #fdf2f8; /* Soft pink background */
        color: #9d174d; /* Dark pink text */
        border-radius: 12px;
        margin-top: 1.5rem;
        border: 1px solid #fbcfe8;
        text-align: center;
    }
    .booking-success a {
        display: inline-block;
        background-color: #25D366;
        color: white;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        margin-top: 15px;
        transition: background-color 0.3s;
    }
    .booking-success a:hover {
        background-color: #128C7E;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE DATABASE ---
db.init_db()

# --- HEADER ---
st.title("Pinky Healthcare Booking ⚕️")
st.markdown("<p class='subtitle'>Book your diagnostic tests quickly with <strong>free transport</strong> and confirm via WhatsApp.</p>", unsafe_allow_html=True)

# --- BOOKING FORM ---
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Patient Full Name", placeholder="e.g., John Doe")
        phone = st.text_input("WhatsApp Number", placeholder="e.g., +919876543210")
    
    with col2:
        # Specialized healthcare options
        service_options = [
            "Blood Test", "MRI Scan", "CT Scan", "ECG", 
            "Ultrasound", "X-Ray", "Echo", "Mammography", "Other"
        ]
        service_type = st.selectbox("Diagnostic Test Required", service_options)
        
        quick_date = st.radio("When do you need it?", ["Today", "Tomorrow", "Custom Date"], horizontal=True)
        if quick_date == "Today":
            date = datetime.date.today()
        elif quick_date == "Tomorrow":
            date = datetime.date.today() + datetime.timedelta(days=1)
        else:
            date = st.date_input("Select Date", min_value=datetime.date.today())
            
        quick_time = st.radio("Preferred Time Slot", ["Morning (9AM-12PM)", "Afternoon (12PM-4PM)", "Evening (4PM-7PM)", "Custom Time"], horizontal=True)
        if quick_time == "Morning (9AM-12PM)":
            time_val = datetime.time(10, 0)
            time_display = "Morning (Between 9 AM - 12 PM)"
        elif quick_time == "Afternoon (12PM-4PM)":
            time_val = datetime.time(14, 0)
            time_display = "Afternoon (Between 12 PM - 4 PM)"
        elif quick_time == "Evening (4PM-7PM)":
            time_val = datetime.time(17, 0)
            time_display = "Evening (Between 4 PM - 7 PM)"
        else:
            time_val = st.time_input("Select Exact Time", value=datetime.time(9, 0))
            time_display = time_val.strftime('%I:%M %p')
    need_transport = st.checkbox("I need the Free Pickup & Drop service 🚕", value=True)

    st.markdown("---")
    
    if st.button("Book Now & Confirm on WhatsApp", use_container_width=True):
        # Basic validation for phone (at least 10 digits, optional +)
        phone_valid = re.match(r'^\+?[\d\s\-]{10,}$', phone)
        
        if not name or not phone:
            st.error("Please fill in both the patient's name and WhatsApp number.")
        elif not phone_valid:
            st.error("Please enter a valid phone number (at least 10 digits).")
        else:
            # Add transport info to the service type for the DB record
            db_service = f"{service_type} (Transport: {'Yes' if need_transport else 'No'})"
            
            # Save to database
            booking_id = db.add_booking(name, phone, db_service, date, time_display)
            
            # Format WhatsApp message
            business_phone = "919892768818" # Phone number from the Next.js page
            
            transport_text = "Yes, please arrange pickup." if need_transport else "No transport needed."
            message = f"Hello Pinky Sharma!\n\nI would like to confirm my diagnostic test booking (ID: {booking_id}).\n\n*Patient Name:* {name}\n*Test:* {service_type}\n*Date:* {date.strftime('%B %d, %Y')}\n*Time:* {time_display}\n*Free Transport:* {transport_text}\n\nThank you!"
            
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{business_phone}?text={encoded_message}"
            
            # Display success message and link
            st.markdown(f"""
                <div class="booking-success">
                    <h3 style="margin-bottom: 10px;">✅ Step 1 Complete!</h3>
                    <p style="font-size: 1.1rem; margin-bottom: 5px;">Your appointment has been securely recorded.</p>
                    <p>Redirecting you to WhatsApp to finalize your slot. If nothing happens, click the button below.</p>
                    <a href="{whatsapp_url}" target="_blank">
                        Complete via WhatsApp 💬
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
            # Auto-redirect via JS injection
            st.components.v1.html(
                f"""
                <script>
                    window.open('{whatsapp_url}', '_blank');
                </script>
                """,
                height=0,
            )
