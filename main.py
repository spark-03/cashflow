import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from urllib.parse import urlencode
from cryptography.fernet import Fernet
import base64
import os
import requests

from fetch_email import get_today_debit_amount  # ✅ Import the debit fetch function

# ─────────────────────────────────────
# Supabase & Encryption Setup
# ─────────────────────────────────────
ENCRYPTION_SECRET_KEY = st.secrets["ENCRYPTION_SECRET_KEY"]
fernet = Fernet(base64.urlsafe_b64encode(ENCRYPTION_SECRET_KEY.encode().ljust(32)[:32]))

# ─────────────────────────────────────
# Google OAuth Setup
# ─────────────────────────────────────
CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = "https://cashflow-spark.streamlit.app"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

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

        email = userinfo.get("email")
        name = userinfo.get("name", "No Name")
        refresh_token = credentials.refresh_token

        st.write("📧 Logged in Email:", email)
        st.write("🔑 Refresh Token:", refresh_token)

        from supabase_utils import store_user_token
        store_user_token(email, refresh_token)

        if not refresh_token:
            st.error("❌ Refresh token missing. Please try again.")
        else:
            encrypted_token = fernet.encrypt(refresh_token.encode()).decode()

            st.success(f"✅ Logged in as {email}")
            st.balloons()

            # ✅ Fetch and display today's debit amount
            debit_amount = get_today_debit_amount(email)
            st.metric("💸 Total Debited Today", f"₹{debit_amount:,.2f}")

    except Exception as e:
        st.error(f"⚠️ Login failed: {e}")
