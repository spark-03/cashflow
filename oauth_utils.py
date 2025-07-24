import streamlit as st
from google_auth_oauthlib.flow import Flow
import os
import json

# Load Google client secrets
CLIENT_SECRETS = {
    "web": {
        "client_id": "YOUR_CLIENT_ID",
        "project_id": "cashflow-project",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "YOUR_CLIENT_SECRET",
        "redirect_uris": ["https://your-streamlit-app.streamlit.app/"]
    }
}

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "email", "profile"]

def login_with_gmail():
    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=CLIENT_SECRETS["web"]["redirect_uris"][0]
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    st.experimental_set_query_params()  # clear URL
    st.markdown(f"[Click here to authorize →]({auth_url})")

def handle_auth_callback():
    query_params = st.query_params
    if "code" not in query_params:
        return None

    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=CLIENT_SECRETS["web"]["redirect_uris"][0]
    )
    flow.fetch_token(code=query_params["code"])
    credentials = flow.credentials

    from googleapiclient.discovery import build
    gmail = build("gmail", "v1", credentials=credentials)
    profile = gmail.users().getProfile(userId='me').execute()

    user_data = {
        "email": profile["emailAddress"],
        "refresh_token": credentials.refresh_token
    }

    from supabase_utils import store_user_token
    store_user_token(user_data["email"], user_data["refresh_token"])

    return user_data
