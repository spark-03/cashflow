import streamlit as st
from supabase import create_client
from cryptography.fernet import Fernet

# Read from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SECRET_KEY = st.secrets["ENCRYPTION_SECRET_KEY"]  # Must be 32-byte Fernet key in base64

# Initialize encryption and Supabase client
fernet = Fernet(SECRET_KEY.encode())
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def encrypt_token(token: str) -> str:
    """Encrypts a refresh token using Fernet"""
    return fernet.encrypt(token.encode()).decode()

def store_user_token(email: str, refresh_token: str):
    """Encrypts and stores (or updates) a user's refresh token in Supabase"""

    st.write(f"📧 Email received: `{email}`")
    st.write(f"🔑 Refresh token received: `{refresh_token}`")

    if not email or not refresh_token:
        st.error("❌ Missing email or refresh token. Skipping insertion.")
        return

    try:
        encrypted = encrypt_token(refresh_token)
        st.write(f"🛡️ Encrypted token starts with: `{encrypted[:10]}...`")

        data = {"email": email, "refresh_token": encrypted}

        # Check if user exists
        existing = supabase.table("users").select("*").eq("email", email).execute()
        st.write(f"🔍 User check result: `{existing}`")

        if existing and existing.data:
            st.info("🔄 User exists. Updating token.")
            supabase.table("users").update(data).eq("email", email).execute()
        else:
            st.info("🆕 New user. Inserting token.")
            supabase.table("users").insert(data).execute()

        st.success("✅ Token stored successfully in Supabase.")

    except Exception as e:
        st.error(f"💥 Exception occurred: {str(e)}")
