import os
import base64
import json
import re
from datetime import datetime, timedelta
import streamlit as st
from supabase import create_client, Client
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GOOGLE_CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Step 1: Fetch refresh_token from Supabase using email
def get_refresh_token(email):
    response = supabase.table("users").select("refresh_token").eq("email", email).single().execute()
    if response.data and "refresh_token" in response.data:
        return response.data["refresh_token"]
    else:
        return None

# Step 2: Get Gmail service using refresh_token
def get_gmail_service(refresh_token):
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )
    creds.refresh(Request())
    service = build('gmail', 'v1', credentials=creds)
    return service

# Step 3: Fetch today's debit transaction amount
def get_today_debit_amount(email):
    refresh_token = get_refresh_token(email)
    if not refresh_token:
        return 0

    service = get_gmail_service(refresh_token)

    # Today's date
    today = datetime.utcnow().date()
    query = f'after:{today} subject:(debited OR debit)'

    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        total_debit = 0

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = msg_data.get('snippet', '').lower()

            # Extract amount using regex
            match = re.search(r'(?:INR|₹|Rs\.?)\s?([\d,]+(?:\.\d{1,2})?)', snippet, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    total_debit += amount
                except:
                    continue

        return total_debit

    except Exception as e:
        print("Error fetching Gmail:", e)
        return 0
