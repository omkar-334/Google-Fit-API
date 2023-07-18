import json
import time
from datetime import datetime
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import csv

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
'''
authorize_url = flow.step1_get_authorize_url()
webbrowser.open(authorize_url)
code = input("Enter code -")
credentials = flow.step2_exchange(code)
# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)'''


fitness_service = build('fitness', 'v1', credentials=creds)
"""
Run through the OAuth flow and retrieve credentials.
Returns a dataset (Users.dataSources.datasets):
https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets
"""

dataset= fitness_service.users().dataSources().datasets().get(userId='me', dataSourceId=DATA_SOURCE, datasetId=DATA_SET).execute()

with open('dataset.txt', 'w') as outfile:
    json.dump(dataset, outfile)

starts,ends,values = [],[],[]

def nanoseconds(nanotime):
    """
    Convert epoch time with nanoseconds to human-readable.
    """
    dt = datetime.fromtimestamp(nanotime // 1000000000)
    return dt.strftime('%H:%M:%S')
for point in dataset["point"]:
    if int(point["startTimeNanos"]) > START:
        starts.append(int(point["startTimeNanos"]))
        ends.append(int(point["endTimeNanos"]))
        values.append(point['value'][0]['intVal'])
rows=[]
a=list(map(lambda x:nanoseconds(x),starts))
b=list(map(lambda x:nanoseconds(x),ends))
for i,j,k in zip(a,b,values):
    print(i,"to",j,"---",k,"steps")
print("Total Steps - ",sum(values))

dict={}
for i,j in zip(a,values):
    if i in dict:
        dict[i]+=j
    else:
        dict[i]=j

