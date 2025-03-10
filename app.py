import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import Flow
import pandas as pd
import requests
from urllib.parse import urlencode
import json
from streamlit_javascript import st_javascript
from streamlit_local_storage import LocalStorage



# Google OAuth setup
# Load OAuth credentials from Streamlit secrets
creds_auth = st.secrets["oauth_credentials"]["json"]

# Use the credentials to authorize the OAuth flow
# REDIRECT_URI = "https://ruqyah-effect-tracker.streamlit.app/"  # Streamlit default local URL
REDIRECT_URI = "http://localhost:8501/"  # Streamlit default local URL

SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]
localS = LocalStorage()

# Authentication
if "out_state" not in st.session_state:
    st.session_state.out_state = False

# Authentication
if "user_email" not in st.session_state:
    st.session_state.user_email =localS.getItem("ruqyah_effect_tracker_user_email")
    
if st.session_state.out_state:
    st_javascript("localStorage.removeItem('ruqyah_effect_tracker_user_email');")
    st.session_state.out_state = False

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
    query_params = st.query_params.to_dict()
    redirect_response = f"{REDIRECT_URI}?{urlencode(query_params)}"

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

# st.write(st.query_params)
# Check if the user is already logged in via query params
if st.session_state.user_email is None or st.session_state.user_email is '0':
    
    authenticate_user()
    if "code" in st.query_params:
        try:
            email, name = get_user_info()
            st.session_state.user_email = email
            st.session_state.user_name = name
            st.query_params["user_email"] = email
            st.query_params["user_name"] = name
            st.query_params.clear()
            st.success(f"Welcome, {name} ({email})!")
            st_javascript(f"localStorage.setItem('ruqyah_effect_tracker_user_email', '{email}');")
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please complete the Google login process.")

else:
    col1, col2 = st.columns([2,1])
    with col1:
        st.success(f"Welcome, {st.session_state.user_email}!")
    with col2:
        if st.button("Logout"):
              # Execute JavaScript first
            st.session_state.user_email = None
            st.session_state.out_state = True
            st.rerun() # Reset session state
    
    # Google Sheets authentication
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["google_credentials"]["json"]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    SHEET_NAME = "Ruqyah Effects"
    sheet = client.open(SHEET_NAME).sheet1

    # Streamlit UI
    st.title("Ruqyah Effects Tracker")

    # Session State for Editing
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = None

    if "show_modal" not in st.session_state:
        st.session_state.show_modal = False

    # Fetch Data from Google Sheets
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df = df[df["Email"]==st.session_state.user_email]

    # Modal for Data Entry Form
    if not st.session_state.show_modal:

        # Display the Recorded Data Table
        st.subheader("Recorded Data")
        # Add Record Button
        if st.button("Add Record"):
            st.session_state.show_modal = True  # Open the modal
            st.session_state.edit_index = None  # Reset edit mode
            st.rerun()  # Refresh the app
                
        if not df.empty:
            st.write("### Recorded Entries:")
            
            # Create Table with Buttons
            for index, row in df.iterrows():
                col1, col2, col3, col4 = st.columns([2, 4, 4, 1])
                
                with col1:
                    st.write(f"**{row['Activity']}** -> {row['Effectiveness']}")
            
                with col2:
                    st.write(f"{row['Problems'][:200]}{'...' if len(row['Problems']) > 200 else ''}")


                with col3:
                    st.write(f"{row['Reactions'][:200]}{'...' if len(row['Reactions']) > 200 else ''}")

                with col4:
                    if st.button(f"✏️", key=f"edit_{index}"):
                        st.session_state.edit_index = index
                        st.session_state.show_modal = True
                        st.rerun()  # Refresh the app
                st.divider()

        else:
            st.info("No data recorded yet.")

    else:
        with st.form("effects_form"):
            st.subheader("Record a New Entry" if st.session_state.edit_index is None else "Edit Entry")
            
            email_value = st.session_state.user_email
            if st.session_state.edit_index is not None:
                
                # Get selected row data
                row_data = df.iloc[st.session_state.edit_index]
                activity_value = row_data["Activity"]
                problems_value = row_data["Problems"]
                duration_value = row_data["Duration"]
                reactions_value = row_data["Reactions"]
                effectiveness_value = row_data["Effectiveness"]
            else:
                activity_value = ""
                problems_value = ""
                duration_value = 1
                reactions_value = ""
                effectiveness_value = 5

            activity = st.text_input("Activity", value=activity_value)
            problems = st.text_area("Pre-Condition", value=problems_value)
            duration = st.number_input("Duration (hours)", min_value=0, value=duration_value)
            reactions = st.text_area("Post-Condition", value=reactions_value)
            effectiveness = st.slider("Effectiveness (0-10)", 0, 10, effectiveness_value)

            submitted = st.form_submit_button("Submit")
            cancel = st.form_submit_button("Cancel")

            if submitted:
                row = [email_value, activity, problems, duration, reactions, effectiveness]
                if st.session_state.edit_index is None:
                    # Append New Entry
                    sheet.append_row(row)
                    st.success("Data submitted successfully!")
                    st.session_state.show_modal = False
                else:
                    sheet.update(range_name=f"A{st.session_state.edit_index+2}:G{st.session_state.edit_index+2}", values=[row])
                    st.success("Data updated successfully!")
                    st.session_state.edit_index = None
                    st.session_state.show_modal = False
                
                st.rerun()

            if cancel:
                st.session_state.edit_index = None
                st.session_state.show_modal = False
                st.rerun()
