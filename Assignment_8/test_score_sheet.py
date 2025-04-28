import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Step 1: Fetch current F1 standings
def get_current_f1_standings():
    url = "https://ergast.com/api/f1/current/driverStandings.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        standings_list = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        
        rows = []
        for driver in standings_list:
            position = driver['position']
            points = driver['points']
            driver_name = driver['Driver']['givenName'] + " " + driver['Driver']['familyName']
            nationality = driver['Driver']['nationality']
            constructor = driver['Constructors'][0]['name']
            
            rows.append([position, driver_name, nationality, constructor, points])
        
        return rows
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def upload_to_google_sheets(data):
    # Authenticate
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials/sheets_credentials.json', scope)
    gc = gspread.authorize(creds)

    # Create a new spreadsheet
    sh = gc.create("F1 Current Standings")

    # Share the spreadsheet
    sh.share(None, perm_type="anyone", role="reader")  # Anyone with the link can view

    # Select the first worksheet
    worksheet = sh.get_worksheet(0)

    # Set headers
    worksheet.append_row(["Position", "Driver", "Nationality", "Constructor", "Points"])

    # Insert the data
    for row in data:
        worksheet.append_row(row)

    # Get the spreadsheet URL
    sheet_url = sh.url
    return sheet_url

# MAIN
if __name__ == "__main__":
    f1_standings = get_current_f1_standings()
    if f1_standings:
        sheet_link = upload_to_google_sheets(f1_standings)
        print(f"\n✅ Data uploaded successfully! Here is your sheet link:\n{sheet_link}")
    else:
        print("❌ No data to upload.")
