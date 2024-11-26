# scripts/restore_postgres.py

import os
import subprocess
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv
import io
import sys

# Load environment variables from .env file
load_dotenv()

# Get environment variables
SERVICE_ACCOUNT_INFO = {
    "type": os.getenv("SERVICE_ACCOUNT_TYPE"),
    "project_id": os.getenv("SERVICE_ACCOUNT_PROJECT_ID"),
    "private_key_id": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY_ID"),
    "private_key": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("SERVICE_ACCOUNT_CLIENT_EMAIL"),
    "client_id": os.getenv("SERVICE_ACCOUNT_CLIENT_ID"),
    "auth_uri": os.getenv("SERVICE_ACCOUNT_AUTH_URI"),
    "token_uri": os.getenv("SERVICE_ACCOUNT_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("SERVICE_ACCOUNT_CLIENT_CERT_URL"),
}
BACKUP_FOLDER = os.getenv("BACKUP_FOLDER")

# Define backup directory and file
BACKUP_DIR = "/Users/bradyespey/Projects/PoGO/backups"
BACKUP_FILE_NAME = "postgres_backup.dump"
BACKUP_FILE = os.path.join(BACKUP_DIR, BACKUP_FILE_NAME)


def download_from_google_drive():
    """Download the backup file from Google Drive."""
    print("Downloading backup file from Google Drive...")

    # Ensure the backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Remove the old backup file if it exists
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)
        print(f"Old backup file '{BACKUP_FILE_NAME}' removed.")

    try:
        credentials = Credentials.from_service_account_info(
            SERVICE_ACCOUNT_INFO,
            scopes=["https://www.googleapis.com/auth/drive.file"]
        )
        drive_service = build("drive", "v3", credentials=credentials)

        # Find the backup file in the specified Google Drive folder
        query = f"'{BACKUP_FOLDER}' in parents and name='{BACKUP_FILE_NAME}' and trashed=false"
        response = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = response.get("files", [])
        if not files:
            print(f"Backup file '{BACKUP_FILE_NAME}' not found in Google Drive.")
            sys.exit(1)

        # Download the backup file
        file_id = files[0]["id"]
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(BACKUP_FILE, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}% complete.")
        print(f"Backup file '{BACKUP_FILE}' downloaded.")

        # Return the file ID for public URL generation
        return file_id, drive_service
    except Exception as e:
        print(f"Error downloading backup file: {e}")
        sys.exit(1)


def generate_public_url(file_id, drive_service):
    """Generate a public URL for the backup file on Google Drive."""
    try:
        # Update the file permissions to be publicly accessible
        permission = {
            "type": "anyone",
            "role": "reader"
        }
        drive_service.permissions().create(fileId=file_id, body=permission).execute()

        # Return the file's public URL
        public_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        print(f"Public URL generated: {public_url}")
        return public_url
    except Exception as e:
        print(f"Error generating public URL: {e}")
        sys.exit(1)


def restore_to_heroku(public_url):
    """Restore the backup to the Heroku PostgreSQL database."""
    print("Restoring PostgreSQL database to Heroku...")
    try:
        # Restore the backup file to Heroku using the public URL
        subprocess.run(
            [
                "heroku", "pg:backups:restore",
                public_url,
                "DATABASE_URL",
                "--app", "pogo",
                "--confirm", "pogo"
            ],
            check=True
        )
        print("Database restored to Heroku successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error restoring database to Heroku: {e}")
        sys.exit(1)


if __name__ == "__main__":
    file_id, drive_service = download_from_google_drive()
    public_url = generate_public_url(file_id, drive_service)
    restore_to_heroku(public_url)