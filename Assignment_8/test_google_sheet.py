import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Step 1: Authenticate
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Step 2: Create a new Sheet    
sheet_title = "Auto Created Sheet"
sheet = client.create(sheet_title)

# Step 3: Share the sheet publicly or with a user
sheet.share(None, perm_type='anyone', role='reader')  # Anyone with link can view

# Step 4: Get the Shareable Link
sheet_id = sheet.id
shareable_link = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?usp=sharing"

print(f"✅ Sheet created successfully!\nShareable Link: {shareable_link}")
