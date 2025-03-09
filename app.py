import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("matrimony-site-2a5ea-14677e796fe6.json", scopes=scope)
client = gspread.authorize(creds)

# Open the Google Sheet
SHEET_NAME = "Ruqyah Effects"
sheet = client.open(SHEET_NAME).sheet1

# Streamlit UI
st.title("Ruqyah Effects")

# Session State for Editing and Modal
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

if "show_modal" not in st.session_state:
    st.session_state.show_modal = False

# Fetch Data from Google Sheets
data = sheet.get_all_records()
df = pd.DataFrame(data)





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
        # Display Table with Edit Buttons
        for index, row in df.iterrows():
            cols = st.columns(8)
            cols[0].write(row["Activity"])
            cols[1].write(row["Before Condition"])  # Ensure this matches the column name in your Google Sheets
            cols[2].write(row["Before Severity"])   # Ensure this matches the column name in your Google Sheets
            cols[3].write(row["Duration"])
            cols[4].write(row["After Condition"])   # Ensure this matches the column name in your Google Sheets
            cols[5].write(row["After Severity"])    # Ensure this matches the column name in your Google Sheets
            cols[6].write(row["Effectiveness"])
            if cols[7].button("✏️ Edit", key=index):
                st.session_state.edit_index = index  # Store row index for editing
                st.session_state.show_modal = True  # Open the modal
                st.rerun()  # Refresh the app
    else:
        st.info("No data recorded yet.")
else:
    with st.form("effects_form"):
        st.subheader("Record a New Entry" if st.session_state.edit_index is None else "Edit Entry")

        # If editing, get selected row data
        if st.session_state.edit_index is not None:
            row_data = df.iloc[st.session_state.edit_index]
            activity_value = row_data["Activity"]
            pre_condition_value = row_data["Before Condition"]  # Ensure this matches the column name in your Google Sheets
            pre_intensity_value = row_data["Before Severity"]   # Ensure this matches the column name in your Google Sheets
            duration_value = row_data["Duration"]
            post_condition_value = row_data["After Condition"]  # Ensure this matches the column name in your Google Sheets
            post_intensity_value = row_data["After Severity"]   # Ensure this matches the column name in your Google Sheets
            effectiveness_value = row_data["Effectiveness"]
        else:
            activity_value = ""
            pre_condition_value = ""
            pre_intensity_value = 5
            duration_value = 1
            post_condition_value = ""
            post_intensity_value = 5
            effectiveness_value = "Very Effective"

        activity = st.text_input("Activity (e.g., Read Quran, Took Medicine)", value=activity_value)
        pre_condition = st.text_area("Pre-Condition (How you felt before)", value=pre_condition_value)
        pre_intensity = st.slider("Pre-Condition Intensity (0-10)", 0, 10, pre_intensity_value)
        duration = st.number_input("Duration (minutes)", min_value=1, value=duration_value)
        post_condition = st.text_area("Post-Condition (How you felt after)", value=post_condition_value)
        post_intensity = st.slider("Post-Condition Intensity (0-10)", 0, 10, post_intensity_value)
        effectiveness = st.selectbox("Effectiveness", ["Very Effective", "Somewhat Effective", "Not Effective"], index=["Very Effective", "Somewhat Effective", "Not Effective"].index(effectiveness_value))
        
        submitted = st.form_submit_button("Submit")
        cancel = st.form_submit_button("Cancel")

        if submitted:
            row = [activity, pre_condition, pre_intensity, duration, post_condition, post_intensity, effectiveness]
            if st.session_state.edit_index is None:
                # Append New Entry
                sheet.append_row(row)
                st.success("Data submitted successfully!")
            else:
                # Update Existing Entry
                sheet.update(range_name=f"A{st.session_state.edit_index+2}:G{st.session_state.edit_index+2}", values=[row])  # Corrected update method
                st.success("Data updated successfully!")
                st.session_state.edit_index = None  # Reset Edit Mode
            st.session_state.show_modal = False  # Close the modal
            st.rerun()  # Refresh the app

        if cancel:
            st.session_state.show_modal = False  # Close the modal
            st.session_state.edit_index = None  # Reset edit mode
            st.rerun()  # Refresh the app