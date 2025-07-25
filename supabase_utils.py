import streamlit as st
from supabase import create_client

# Load from secrets manager
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]  # Use service role key

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_user_token(email: str, refresh_token: str):
    """Securely stores or updates a Gmail refresh token in Supabase"""
    if not email or not refresh_token:
        st.error("Missing email or token.")
        return

    try:
        data = {"email": email, "refresh_token": refresh_token}
        existing = supabase.table("users").select("*").eq("email", email).execute()

        if existing.data:
            supabase.table("users").update(data).eq("email", email).execute()
        else:
            supabase.table("users").insert(data).execute()

        st.success("Token stored securely.")
    except Exception as e:
        st.error(f"Error storing token: {str(e)}")
