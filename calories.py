from flask import Flask, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time
from datetime import datetime
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import json

# Copy your credentials from the Google Developers Console
CLIENT_ID = '264617833817-3ogggshae5i2ccjo54ilsv80m8muuhuk.apps.googleusercontent.com'
CLIENT_SECRET = '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'

# Check https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get
# for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read'

# DATA SOURCE
DATA_SOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
# The ID is formatted like: "startTime-endTime" where startTime and endTime are
# 64 bit integers (epoch time with nanoseconds).
TODAY = datetime.today().date()
NOW = datetime.today()
START = int(time.mktime(TODAY.timetuple())*1000000000)
END = int(time.mktime(NOW.timetuple())*1000000000)
DATA_SET = "%s-%s" % (START, END)


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
            'credentials.json', OAUTH_SCOPE)
        creds = flow.run_console()
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)

fitness = build('fitness', 'v1', credentials=creds)

response = fitness.users().dataset().aggregate(
    userId='me',
    body={
        'aggregateBy': [
            {'dataTypeName': 'com.google.calories.expended'},
            #{'dataTypeName': 'com.google.heart_rate.bpm'}
        ],
        'bucketByTime': {'durationMillis': 86400000},
        'startTimeMillis': int(time.time() * 1000) - 86400000,
        'endTimeMillis': int(time.time() * 1000)
    }
).execute()

calories_burnt = response['bucket'][0]['dataset'][0]['point'][0]['value'][0]['fpVal']
#heart_rate = response['bucket'][0]['dataset'][1]['point'][0]['value'][0]['fpVal']
with open('calories.json', 'w') as f:
    json.dump({'calories_burnt': calories_burnt}, f)
