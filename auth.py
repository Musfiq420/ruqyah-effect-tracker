import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allow HTTP for local testing

import streamlit as st
from google_auth_oauthlib.flow import Flow
import requests
from urllib.parse import urlencode

# Google OAuth setup
# Load OAuth credentials from Streamlit secrets
creds_auth = st.secrets["oauth_credentials"]["json"]

# Use the credentials to authorize the OAuth flow
REDIRECT_URI = "http://localhost:8501/"  # Streamlit default local URL
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

# Authentication
if "user_email" not in st.session_state:
    st.session_state.user_email = None

def authenticate_user():
    """Start the OAuth authentication flow"""
    flow = Flow.from_client_config(
        creds_auth, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(prompt="consent")
    st.session_state.oauth_state = state
    st.write(f"[Click here to login with Google]({auth_url})")

def get_user_info():
    """Fetch user info after authentication"""
    # Construct the full redirect URL from query parameters
    query_string = urlencode(st.query_params.to_dict())
    redirect_response = f"{REDIRECT_URI}?{query_string}"

    # Initialize the OAuth flow
    flow = Flow.from_client_config(
        creds_auth, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )

    # Fetch the token using the full redirect URL
    flow.fetch_token(authorization_response=redirect_response)

    # Get user info
    credentials = flow.credentials
    user_info_endpoint = "https://www.googleapis.com/oauth2/v2/userinfo"
    user_info = requests.get(user_info_endpoint, headers={"Authorization": f"Bearer {credentials.token}"}).json()
    
    return user_info["email"], user_info["name"]

# Debugging: Print query parameters
st.write("Query Parameters:", st.query_params)

if st.session_state.user_email is None:
    authenticate_user()
    if "code" in st.query_params:
        try:
            email, name = get_user_info()
            st.session_state.user_email = email
            st.session_state.user_name = name
            st.success(f"Welcome, {name} ({email})!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please complete the Google login process.")

if st.session_state.user_email:
    st.write(f"Logged in as: {st.session_state.user_email}")
    # Add your app logic here