import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from supabase import create_client, Client
from urllib.parse import urlencode
from cryptography.fernet import Fernet
import base64
import os
import requests

# ─────────────────────────────────────
# Supabase & Encryption Setup
# ─────────────────────────────────────
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ENCRYPTION_SECRET_KEY = st.secrets["ENCRYPTION_SECRET_KEY"]

# Setup Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Encryption setup (must be 32 bytes for Fernet)
fernet = Fernet(base64.urlsafe_b64encode(ENCRYPTION_SECRET_KEY.encode().ljust(32)[:32]))

# ─────────────────────────────────────
# Google OAuth Setup
# ─────────────────────────────────────
CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = "https://cashflow-spark.streamlit.app"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "openid", "email", "profile"]

# ─────────────────────────────────────
# UI
# ─────────────────────────────────────
st.set_page_config(page_title="Cashflow Mail Login", page_icon="📬")
st.title("📬 Cashflow Mail Login")

# Step 1: Show login button
if "credentials" not in st.session_state:
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode({
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'
    })}"
    st.markdown(f"[🔐 Login with Gmail]({auth_url})")

# Step 2: Handle Google redirect
query_params = st.experimental_get_query_params()
if "code" in query_params:
    code = query_params["code"][0]

    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uris": [REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Get user info from Google
        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"access_token": credentials.token}
        ).json()

        email = userinfo["email"]
        name = userinfo.get("name", "No Name")
        refresh_token = credentials.refresh_token

        if not refresh_token:
            st.error("❌ Refresh token missing. Please try again.")
        else:
            # Encrypt and save to Supabase
            encrypted_token = fernet.encrypt(refresh_token.encode()).decode()

            existing_user = supabase.table("users").select("id").eq("email", email).execute()

            if existing_user.data:
                supabase.table("users").update({
                    "refresh_token_encrypted": encrypted_token,
                    "name": name
                }).eq("email", email).execute()
            else:
                supabase.table("users").insert({
                    "email": email,
                    "name": name,
                    "refresh_token_encrypted": encrypted_token
                }).execute()

            st.success(f"✅ Logged in as {email}")
            st.balloons()

    except Exception as e:
        st.error(f"⚠️ Login failed: {e}")
