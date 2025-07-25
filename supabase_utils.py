import streamlit as st
from supabase import create_client

# Read from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_user_token(email: str, refresh_token: str):
    """Stores (or updates) a user's refresh token in Supabase"""
    st.write(f"📧 Email received: `{email}`")
    st.write(f"🔑 Refresh token received: `{refresh_token}`")

    if not email or not refresh_token:
        st.error("❌ Missing email or refresh token. Skipping insertion.")
        return

    try:
        data = {"email": email, "refresh_token": refresh_token}

        # Check if user already exists
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
