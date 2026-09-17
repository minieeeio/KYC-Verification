import os
import pickle
import logging
import sys

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth import exceptions as google_auth_exception
from googleapiclient.errors import HttpError

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET_KEY=os.getenv("CLIENT_SECRET")
SCOPES=["https://www.googleapis.com/auth/drive"]
TOKEN_PATH="token.pickle"

class DriveAuthError(google_auth_exception.GoogleAuthError):
    pass


class DriveAPI(object):
    def __init__(self):
        print("Initlization of OAuth Google Drive API")
        print(os.path.abspath(TOKEN_PATH))
        self.service=None
        
    def authenticate_credentials(self):
        try:
            creds=None
                    
            if os.path.exists(TOKEN_PATH):
                            with open(TOKEN_PATH,"rb") as token_file:
                                creds=pickle.load(token_file)
                                 
            if not creds or not creds.valid:
                            if creds and creds.expired and creds.refresh_token:
                                    creds.refresh(Request())
                            else:
                                flow=InstalledAppFlow.from_client_secrets_file("credentials.json",SCOPES)
                                creds=flow.run_local_server(port=0,timeout_seconds=120)
                    
            try:
                with open(TOKEN_PATH,"wb") as token_file:
                                    pickle.dump(creds,token_file)
            except Exception as e:
                        print(f"WARNING: failed to save token.pick{e}") 
                          
            self.service=build("drive","v3",credentials=creds)
            return self.service
        except google_auth_exception.GoogleAuthError as e:
            logging.error(f"FATAL: Google Drive Authentication/Permission Error,{e}")
            raise DriveAuthError(f"Drive authentication failed: {e}") from e
        
    def retrieve_files(self):
        # try:
        #     self.service=
        pass

                
            
    
        