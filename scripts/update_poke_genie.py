import os
import sys
from pathlib import Path
import csv
import time
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Add the project root directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Now, you can import app and models after sys.path is correctly set
from app import app, db
from models import PokeGenieEntry

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1--T8Abai5H-b8vY_OVAVHKdA4NXC50rS'

# Get Google API credentials from environment variables
SERVICE_ACCOUNT_INFO = {
    "type": os.getenv('GOOGLE_TYPE'),
    "project_id": os.getenv('GOOGLE_PROJECT_ID'),
    "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
    "client_id": os.getenv('GOOGLE_CLIENT_ID'),
    "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
    "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_CERT_URL'),
    "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_CERT_URL'),
}

# Create Google API credentials
creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

def download_latest_csv_from_drive():
    """Download the latest CSV file from Google Drive"""
    print(f"Using folder ID: {FOLDER_ID}")

    results = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType='text/csv'",
        orderBy="createdTime desc",
        pageSize=1,
        fields="files(id, name)"
    ).execute()

    if 'files' not in results or not results['files']:
        raise FileNotFoundError("No CSV file found in the folder.")

    file = results['files'][0]
    file_id = file['id']
    file_name = file['name']
    destination = f"/tmp/{file_name}"

    print(f"Downloading file {file_name}...")

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}% complete.")

    print(f"File downloaded to {destination}")
    return destination

def import_poke_genie_data(app_context):
    with app_context:
        csv_file_path = download_latest_csv_from_drive()
        if not csv_file_path:
            print("No CSV file found. Exiting.")
            return

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # Skip header

            total_entries = sum(1 for row in reader)
            print(f"Found {total_entries} Poke Genie entries in the CSV.")

            csvfile.seek(0)
            next(reader)  # Skip header again after reset

            count_inserted, count_skipped = 0, 0

            for idx, row in enumerate(reader):
                index = int(row[0])
                name = row[1]
                pokemon_number = int(row[3])

                existing_entry = PokeGenieEntry.query.filter_by(index=index).first()

                if existing_entry:
                    count_skipped += 1
                else:
                    new_entry = PokeGenieEntry(
                        index=index,
                        name=name,
                        pokemon_number=pokemon_number,
                        # Add other fields here
                    )
                    db.session.add(new_entry)
                    db.session.commit()
                    count_inserted += 1

                # Log progress every 10 entries
                if idx % 10 == 0:
                    print(f"Processing entry {idx + 1}/{total_entries}...")

            print(f"Total Poke Genie entries processed: {total_entries}")
            print(f"Entries added: {count_inserted}")
            print(f"Entries skipped: {count_skipped}")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        import_poke_genie_data(app.app_context())