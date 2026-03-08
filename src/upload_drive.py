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
        raise FileNotFoundError(
            f"'{SERVICE_ACCOUNT_FILE}' no encontrado en la raíz del proyecto. "
            "No se puede subir a Google Drive."
        )

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def update_file():
    """Uploads the local Excel file to Google Drive, updating the existing file."""
    print("[DRIVE] Starting upload process...")
    
    # Verify local file exists
    if not os.path.exists(LOCAL_FILE):
        raise FileNotFoundError(
            f"Archivo local '{LOCAL_FILE}' no encontrado. "
            "¿Se generó el reporte correctamente?"
        )

    # Verify configuration
    if not FILE_ID:
        raise ValueError(
            "GOOGLE_DRIVE_FILE_ID no está configurado en .env"
        )

    creds = authenticate()

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