from google.oauth2 import InstalledAppCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os.path
import pickle

# Scopes required for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    # Token file stores the user's access and refresh tokens, and is created automatically
    # when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Define the event
    event = {
        'summary': 'Sample Meeting',
        'description': 'A sample meeting created with the Google Calendar API.',
        'start': {
            'dateTime': (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'conferenceData': {
            'createRequest': {
                'requestId': 'some-random-id',
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet',
                },
            },
        },
        'reminders': {
            'useDefault': True,
        },
    }

    # Create the event
    event_result = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1,
        fields='id,conferenceData',
    ).execute()

    print(f"Event created: {event_result.get('htmlLink')}")
    print(f"Google Meet link: {event_result.get('conferenceData', {}).get('entryPoints', [])[0].get('uri')}")

if __name__ == '__main__':
    main()
