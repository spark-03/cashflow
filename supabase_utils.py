import streamlit as st
from supabase import create_client
from cryptography.fernet import Fernet

# Read from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SECRET_KEY = st.secrets["ENCRYPTION_SECRET"]  # Must be 32-byte Fernet key in base64

# Initialize encryption and Supabase client
fernet = Fernet(SECRET_KEY.encode())
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def encrypt_token(token: str) -> str:
    """Encrypts a refresh token using Fernet"""
    return fernet.encrypt(token.encode()).decode()

def store_user_token(email: str, refresh_token: str):
    """Encrypts and stores (or updates) a user's refresh token in Supabase"""

    print(f"[DEBUG] Email received: {email}")
    print(f"[DEBUG] Refresh token received: {refresh_token}")

    if not email or not refresh_token:
        print("[ERROR] Missing email or refresh token. Skipping insertion.")
        return

    try:
        encrypted = encrypt_token(refresh_token)
        print(f"[DEBUG] Encrypted token: {encrypted[:10]}...")  # show only start of encrypted string

        data = {"email": email, "refresh_token": encrypted}

        # Check if user exists
        existing = supabase.table("users").select("*").eq("email", email).execute()
        print(f"[DEBUG] Existing user check result: {existing}")

        if existing and existing.data:
            print("[INFO] User exists. Updating token.")
            supabase.table("users").update(data).eq("email", email).execute()
        else:
            print("[INFO] New user. Inserting token.")
            supabase.table("users").insert(data).execute()

        print("[SUCCESS] Token stored successfully in Supabase.")

    except Exception as e:
        print(f"[EXCEPTION] Failed to store token: {str(e)}")
