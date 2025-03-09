import gspread
from google.oauth2.service_account import Credentials

# Define scope
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials
creds = Credentials.from_service_account_file("matrimony-site-2a5ea-14677e796fe6.json", scopes=SCOPE)
client = gspread.authorize(creds)

# Open the Google Sheet
SHEET_NAME = "Musfiq's Habit Calendar"  # Change to your actual sheet name
sheet = client.open(SHEET_NAME).sheet1  # Opens the first sheet

# Test writing data
test_data = ["Test Activity", "Before Condition", 5, "After Condition", 3, "Effective"]
sheet.append_row(test_data)

# Test reading data
data = sheet.get_all_records()
print("Sheet Data:", data)
