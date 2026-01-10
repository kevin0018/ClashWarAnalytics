import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Ensure project root is in python path to import src.config correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config

# CONSTANTS
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
LOCAL_FILE = 'CWL_History.xlsx'
FILE_ID = Config.GOOGLE_DRIVE_FILE_ID

def authenticate():
    """Authenticates with Google using the service account JSON file."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"[ERROR] '{SERVICE_ACCOUNT_FILE}' not found in project root.")
        return None

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def update_file():
    """Uploads the local Excel file to Google Drive, updating the existing file."""
    print("[DRIVE] Starting upload process...")
    
    # Verify local file exists
    if not os.path.exists(LOCAL_FILE):
        print(f"[ERROR] Local file '{LOCAL_FILE}' not found.")
        print("Hint: Has main.py been executed successfully?")
        return

    # Verify configuration
    if not FILE_ID:
        print("[ERROR] GOOGLE_DRIVE_FILE_ID is missing in .env configuration.")
        return

    creds = authenticate()
    if not creds:
        return

    try:
        # Build Drive API service
        service = build('drive', 'v3', credentials=creds)

        # Prepare file metadata and content
        media = MediaFileUpload(
            LOCAL_FILE, 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=True
        )

        print(f"[DRIVE] Updating file with ID: {FILE_ID}...")

        # Update the existing file content
        updated_file = service.files().update(
            fileId=FILE_ID,
            media_body=media
        ).execute()
        
        print(f"[SUCCESS] File updated successfully. ID: {updated_file.get('id')}")
        
    except Exception as e:
        print(f"[ERROR] Failed to upload to Drive: {e}")
        print("Hint: Ensure the Service Account email has 'Editor' access to the file.")

if __name__ == '__main__':
    update_file()