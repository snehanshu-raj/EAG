import os.path
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
        print(f"Message sent to {to} Message Id: {send_message['id']}")
    except HttpError as error:
        print(f"An error occurred: {error}")

def main():
    """Shows basic usage of the Gmail API. Sends an email to the specified recipient."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "gmail_credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

        # Set your details
        sender = "snehanshu.usc@gmail.com"  # Replace with your email
        to = "snehanshu.usc@gmail.com"  # Replace with recipient's email
        subject = "Test Email"
        body = "This is a test email sent from the Gmail API."

        send_email(service, sender, to, subject, body)

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
