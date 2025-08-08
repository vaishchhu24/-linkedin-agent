import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from datetime import datetime
import os

# Scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def authenticate():
    creds = None
    token_file = 'token.pickle'

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return gspread.authorize(creds)

def log_post_to_sheet(topic, reddit_insights, post_content):
    client = authenticate()
    sheet = client.open("LinkedIn Posts Log").sheet1  # Your Sheet name

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, topic, reddit_insights, post_content]
    sheet.append_row(row)
