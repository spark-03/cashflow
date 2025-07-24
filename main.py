import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import os
import base64
import json
import requests
from urllib.parse import urlencode
from cryptography.fernet import Fernet
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Encryption key setup
ENCRYPTION_SECRET_KEY = os.getenv("ENCRYPTION_SECRET_KEY")
fernet = Fernet(base64.urlsafe_b64encode(ENCRYPTION_SECRET_KEY.encode().ljust(32)[:32]))

# Google OAuth config
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "openid", "email", "profile"]
REDIRECT_URI = "http://localhost:8501"

# UI: Login button
st.title("📬 Cashflow Mail Login")

if "credentials" not in st.session_state:
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode({
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'
    })}"

    st.markdown(f"[Login with Gmail]({auth_url})")

# Step 2: After redirect (parse code from URL)
query_params = st.experimental_get_query_params()
if "code" in query_params:
    code = query_params["code"][0]

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

    # Get user email
    userinfo = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"access_token": credentials.token}
    ).json()

    email = userinfo["email"]
    name = userinfo.get("name", "No Name")
    refresh_token = credentials.refresh_token

    if refresh_token is None:
        st.error("Refresh token is missing. Please try logging in again.")
    else:
        encrypted_token = fernet.encrypt(refresh_token.encode()).decode()

        # Save to Supabase
        existing = supabase.table("users").select("id").eq("email", email).execute()
        if existing.data:
            supabase.table("users").update({
                "refresh_token_encrypted": encrypted_token,
                "name": name,
            }).eq("email", email).execute()
        else:
            supabase.table("users").insert({
                "email": email,
                "name": name,
                "refresh_token_encrypted": encrypted_token
            }).execute()

        st.success(f"Logged in as {email}")
        st.balloons()
