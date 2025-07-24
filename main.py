import streamlit as st
from oauth_utils import login_with_gmail, handle_auth_callback
from supabase_utils import store_user_token

st.set_page_config(page_title="Cashflow", layout="centered")
st.title("💸 Cashflow – Gmail Login")

# 1. Check if redirected from Google
if "code" in st.query_params:
    user_data = handle_auth_callback()
    if user_data:
        st.success(f"Welcome {user_data['email']}")
    else:
        st.error("Login failed. Try again.")

# 2. Show login button
else:
    st.info("Login with your Gmail to fetch transaction data.")
    if st.button("🔐 Login with Gmail"):
        login_with_gmail()
