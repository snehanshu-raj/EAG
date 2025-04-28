from mcp.server.fastmcp import FastMCP
import os
import mcp
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
import base64
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs.log",
    format='%(asctime)s - %(process)d - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

mcp = FastMCP(
    name="Telegram",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)

@mcp.tool()
async def get_current_f1_standings() -> dict:
    """Fetches the latest F1 standings and writes the data in google sheets. Returns the sheet link."""
    url = "https://ergast.com/api/f1/current/driverStandings.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        standings_list = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        
        data = {}
        for i, driver in enumerate(standings_list):
            position = driver['position']
            points = driver['points']
            driver_name = driver['Driver']['givenName'] + " " + driver['Driver']['familyName']
            nationality = driver['Driver']['nationality']
            constructor = driver['Constructors'][0]['name']
            
            data[i] = [position, driver_name, nationality, constructor, points]

        logger.info(f"Standings fetched: {data}")
        return data
    else:
        logger.error(f"Failed to fetch data. Status code: {response.status_code}")
        return {}

@mcp.tool()
async def upload_data_to_sheets(data: dict) -> str:
    logger.info(f"data: {data}, type: {type(data)}")
    """Writes the data to Google Sheets and returns the link of the Sheet"""
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
    for key, val in data.items():
        logger.info(f"val: {val}, type: {type(val)}")
        worksheet.append_row(val)

    # Get the spreadsheet URL
    sheet_url = sh.url
    return sheet_url

@mcp.tool()
async def send_email(link: str, recepient: str) -> str:
    """
    Sends the link as email using Gmail API.
    
    Parameters:
    - link (str): link to be emailed
    - recepient (str): email address to which the link has to be emailed
    
    Example:
        send_email("https:docs.google.com", "abc@example.com")
    """
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    def create_message(sender, to, subject, message_text):
        """Create a message for an email."""
        message = MIMEMultipart()
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject
        msg = MIMEText(message_text)
        message.attach(msg)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return {"raw": raw_message}

    def send_email(service, sender, to, subject, body):
        """Send an email message."""
        try:
            message = create_message(sender, to, subject, body)
            send_message = service.users().messages().send(userId="me", body=message).execute()
            logger.info(f"Message sent to {to} Message Id: {send_message['id']}")
        except HttpError as error:
            logger.info(f"An error occurred: {error}")

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("credentials/token.json"):
        creds = Credentials.from_authorized_user_file("credentials/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/token.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("credentials/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

        # Set your details
        sender = "snehanshu.usc@gmail.com"  # Replace with your email
        to = recepient  # Replace with recipient's email
        subject = "Test Email"
        body = link
        send_email(service, sender, to, subject, body)
        logger.info("Email sent")
        
        return "Message sent"
    except HttpError as error:
        logger.info(f"An error occurred: {error}")
        return f"Exception as: {error}"

@mcp.tool()
async def finish_task(message: str):
    """Terminates the agent execution by either saying if the search was sucessfull or not."""
    return {"response": message}

if __name__ == "__main__":
    logger.info("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="sse")  # Run with stdio for direct execution

    # asyncio.run(main())
