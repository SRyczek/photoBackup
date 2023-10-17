
import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

folder_dir = 'D:/Untitled Export/Untitled Export/'
cloud_folder_dir = "zdjecia"

creds = None
latest_date = None
last_date = None
full_dir = None

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else: 
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES)
        creds = flow.run_local_server(port = 0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    service = build("drive", "v3", credentials=creds)

    response = service.files().list(
        q="name='zdjecia' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive'
    ).execute()

    if not response['files']:
        file_metadata = {
            "name": "zdjecia",
            "mimeType": "application/vnd.google-apps.folder"
        }

        file = service.files().create(body=file_metadata, fields="id").execute()

        folder_id = file.get('id')
    else:
        folder_id = response['files'][0]['id']

    # choose and upload file
    for file in os.listdir(folder_dir):
        full_dir = os.path.join(folder_dir, file)
        modification_date = os.path.getctime(full_dir)
        
        if latest_date is None or modification_date > latest_date:
            latest_date = modification_date 
            latest_dir = os.path.join(folder_dir, file)
            file_metadata = {
                "name": file,
                "parents": [folder_id]
            }      
    media = MediaFileUpload(latest_dir)  
    upload_file = service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields="id").execute()
    print("Backed up file: " + file + "from dir: " + full_dir)

except HttpError as e:
    print("Error: " + str(e))