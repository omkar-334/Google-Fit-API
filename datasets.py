import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import time
from datetime import datetime
from datetime import timedelta

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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
            creds = flow.run_console()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    fit = build('fitness', 'v1', credentials=creds)

    DATA_SOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
    # The ID is formatted like: "startTime-endTime" where startTime and endTime are
    # 64 bit integers (epoch time with nanoseconds).
    TODAY = datetime.today().date()
    NOW = datetime.today()
    START = int(time.mktime(TODAY.timetuple())*1000000000)
    END = int(time.mktime(NOW.timetuple())*1000000000)
    DATA_SET = "%s-%s" % (START, END)

    # Call the Drive v3 API
    response = fit.users().dataSources().list(userId='me').execute()
    #https://www.googleapis.com/fitness/v1/users/me/dataSources
    response2=fit.users().dataSources(). \
              datasets(). \
              get(userId='me', dataSourceId=DATA_SOURCE, datasetId=DATA_SET). \
              execute()
    print(response)
    
    print(response2)

if __name__ == '__main__':
    main()