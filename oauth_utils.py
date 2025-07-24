import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# ✅ Replace these with real secrets using st.secrets
CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

# ✅ Proper Google client config
CLIENT_SECRETS = {
    "web": {
        "client_id": CLIENT_ID,
        "project_id": "cashflow-project",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": CLIENT_SECRET,
        "redirect_uris": [REDIRECT_URI]
    }
}

def login_with_gmail():
    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(
        prompt='consent',
        access_type='offline',
        include_granted_scopes='true'
    )
    st.markdown(f"[Click here to authorize →]({auth_url})")

def handle_auth_callback():
    query_params = st.experimental_get_query_params()

    if "code" not in query_params:
        return None

    code = query_params["code"][0]

    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials

    gmail = build("gmail", "v1", credentials=credentials)
    profile = gmail.users().getProfile(userId='me').execute()

    user_data = {
        "email": profile["emailAddress"],
        "refresh_token": credentials.refresh_token
    }

    from supabase_utils import store_user_token
    store_user_token(user_data["email"], user_data["refresh_token"])

    return user_data
