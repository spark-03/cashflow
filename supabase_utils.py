import streamlit as st
from supabase import create_client

# Read Supabase credentials from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_user_token(email: str, refresh_token: str):
    """Stores or updates a user's refresh token in Supabase."""

    if not email or not refresh_token:
        st.error("❌ Missing email or refresh token. Skipping.")
        return

    try:
        data = {
            "email": email,
            "refresh_token": refresh_token
        }

        # Check if user already exists in the table
        result = supabase.table("users").select("id").eq("email", email).execute()

        if result.status_code != 200:
            st.error("❌ Failed to query Supabase.")
            return

        if result.data:
            # User exists: Update their refresh token
            update_result = supabase.table("users").update(data).eq("email", email).execute()
            if update_result.status_code == 200:
                st.success("🔄 Refresh token updated in Supabase.")
            else:
                st.error("❌ Failed to update token.")
        else:
            # New user: Insert email and token
            insert_result = supabase.table("users").insert(data).execute()
            if insert_result.status_code == 201:
                st.success("🆕 New user token inserted in Supabase.")
            else:
                st.error("❌ Failed to insert new token.")

    except Exception as e:
        st.error(f"💥 Error while saving to Supabase: {e}")
