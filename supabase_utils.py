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
    encrypted = encrypt_token(refresh_token)
    data = {"email": email, "refresh_token": encrypted}

    # Check if user exists
    existing = supabase.table("users").select("*").eq("email", email).execute()

    if existing and existing.data:
        supabase.table("users").update(data).eq("email", email).execute()
    else:
        supabase.table("users").insert(data).execute()
