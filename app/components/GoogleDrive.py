import os
import logging
import sys
import io

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth import exceptions as google_auth_exception
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload

from dotenv import load_dotenv
load_dotenv()


from Constants import  KYC_FOLDERID, INPUT_DIR

SCOPES=["https://www.googleapis.com/auth/drive"]




class DriveAuthError(google_auth_exception.GoogleAuthError):
    pass


class DriveAPI(object):
    def __init__(self):
        print("Initlization of OAuth Google Drive API")
        self.service=None
        
    def authenticate_credentials(self):
        try:
            credentials=service_account.Credentials.from_service_account_file(
                            "service_account_credentials.json",
                            scopes=SCOPES
                        )
                          
            self.service=build("drive","v3",credentials=credentials)
            return self.service
        except google_auth_exception.GoogleAuthError as e:
            logging.error(f"FATAL: Google Drive Authentication/Permission Error,{e}")
            raise DriveAuthError(f"Drive authentication failed: {e}") from e
        
    def list_files(self,folder_id=KYC_FOLDERID,page_token=None):
        # print(self.service)
        # print(folder_id)
        mime_query=(
            f"'{folder_id}' in parents and "
            "mimeType = 'application/pdf' or "
            "mimeType = 'image/png' or "
            "mimeType = 'image/jpeg' "
            )
        all_files=[]
        try:
            while True:
                results=self.service.files().list(
                                q=mime_query,
                                fields="nextPageToken, files(id, name, mimeType, md5Checksum)",
                                pageToken=page_token
                            ).execute()

                files=results.get("files",[])
                all_files.extend(files)
                            
                page_token=results.get("nextPageToken")
                            
                if not page_token:
                    break      
            
        except HttpError as e:
            # print(f"Error: Drive API request failed ({e.resp.status}) :{e}")
            logging.error(f"Error: Drive API request failed ({e.resp.status}) :{e}")
            sys.exit()
        
        if not all_files:
            print("No matching files found.")
        else:
            print(f"Found {len(all_files)} files:\n")
            for f in all_files:
                print(f"- {f['name']}  ({f['mimeType']})  id={f['id']} ")
    
        return all_files
    
    def download_files(self,file_id,file_name):
        os.makedirs(INPUT_DIR,exist_ok=True)
        destination_path=os.path.join(INPUT_DIR, file_name)
        
        try:
            request=self.service.files().get_media(fileId=file_id)
            with io.FileIO(destination_path,"wb") as fh:
                downloader=MediaIoBaseDownload(fh,request)
                done=False
                while not done:
                    status,done=downloader.next_chunk()
                    if status:
                        print(f"Download progress for {file_name}: {int(status.progress() * 100)}%")
            return destination_path
        
        except HttpError as e:
            logging.error(f"ERROR: Drive download failed for {file_name} ({e.resp.status}): {e}")
            if os.path.exists(destination_path):
                os.remove(destination_path)
                raise
        
        except Exception as e:
            logging.error(f"ERROR: Download failed for {file_name}: {e}")
        if os.path.exists(destination_path):
            os.remove(destination_path)
        raise
    
    def get_or_create_subfolder(self, folder_name: str, parent_folder_id: str) -> str:
        if not hasattr(self, "_subfolder_cache"):
            self._subfolder_cache = {}

        cache_key = (parent_folder_id, folder_name)
        if cache_key in self._subfolder_cache:
            return self._subfolder_cache[cache_key]

        query = (
            f"'{parent_folder_id}' in parents and "
            f"name = '{folder_name}' and "
            "mimeType = 'application/vnd.google-apps.folder' and "
            "trashed = false"
        )
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        existing = results.get("files", [])

        if existing:
            folder_id = existing[0]["id"]
        else:
            metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_folder_id],
            }
            created = self.service.files().create(body=metadata, fields="id").execute()
            folder_id = created["id"]

        self._subfolder_cache[cache_key] = folder_id
        return folder_id


    def move_file(self, file_id: str, status: str, source_folder_id: str = None):
        if source_folder_id is None:
            source_folder_id = os.getenv("FOLDER_ID")

        destination_folder_id = self.get_or_create_subfolder(status, source_folder_id)

        try:
            self.service.files().update(
                fileId=file_id,
                addParents=destination_folder_id,
                removeParents=source_folder_id,
                fields="id, parents",
            ).execute()
        except HttpError as e:
            print(f"ERROR: Drive move failed for file {file_id} ({e.resp.status}): {e}")
            raise
    
    
        
                            
            
                
            
    
        