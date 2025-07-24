from supabase import create_client
import os
from cryptography.fernet import Fernet

SUPABASE_URL = "https://xyzcompany.supabase.co"
SUPABASE_KEY = "your_supabase_anon_key"
SECRET_KEY = b"your_32_byte_generated_fernet_key"  # use Fernet.generate_key()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
fernet = Fernet(SECRET_KEY)

def encrypt_token(token):
    return fernet.encrypt(token.encode()).decode()

def store_user_token(email, refresh_token):
    encrypted = encrypt_token(refresh_token)
    data = {"email": email, "refresh_token": encrypted}
    existing = supabase.table("users").select("*").eq("email", email).execute()

    if existing.data:
        supabase.table("users").update(data).eq("email", email).execute()
    else:
        supabase.table("users").insert(data).execute()
