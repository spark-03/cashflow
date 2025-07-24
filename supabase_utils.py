from supabase import create_client
import os
from cryptography.fernet import Fernet

# It's better to read secrets from environment variables (e.g., Streamlit secrets)
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]
SECRET_KEY = os.getenv("ENCRYPTION_SECRET") or st.secrets["ENCRYPTION_SECRET"]

# Ensure SECRET_KEY is in bytes
fernet = Fernet(SECRET_KEY.encode())

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def store_user_token(email: str, refresh_token: str):
    encrypted = encrypt_token(refresh_token)
    data = {"email": email, "refresh_token": encrypted}

    # Check if email already exists
    existing = supabase.table("users").select("*").eq("email", email).execute()

    if existing.data:
        supabase.table("users").update(data).eq("email", email).execute()
    else:
        supabase.table("users").insert(data).execute()
