# scripts/backup_postgres.py

import os
import sys
import subprocess
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from sqlalchemy import create_engine, inspect, Table, MetaData, select
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

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

TEMP_DB_NAME = "temp_db"
TEMP_DB_URL = f"postgresql://localhost/{TEMP_DB_NAME}"

def backup_database():
    print("Backing up PostgreSQL database in Heroku...")

    # Ensure the backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Remove the old backup file if it exists
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)
        print(f"Old backup file '{BACKUP_FILE_NAME}' removed.")

    try:
        # Create the backup on Heroku
        subprocess.run(
            ["heroku", "pg:backups:capture", "-a", "pogo"],
            check=True
        )
        print("Backup created in Heroku.")

        # Download the latest backup
        subprocess.run(
            ["heroku", "pg:backups:download", "-a", "pogo", "--output", BACKUP_FILE],
            check=True
        )
        print(f"Backup downloaded locally as {BACKUP_FILE}.")
    except subprocess.CalledProcessError as e:
        print(f"Error during PostgreSQL backup: {e}")
        sys.exit(1)

def upload_to_google_drive():
    print("Uploading backup to Google Drive...")
    try:
        credentials = Credentials.from_service_account_info(
            SERVICE_ACCOUNT_INFO,
            scopes=["https://www.googleapis.com/auth/drive.file"]
        )
        drive_service = build("drive", "v3", credentials=credentials)

        file_metadata = {
            "name": BACKUP_FILE_NAME,
            "parents": [BACKUP_FOLDER]
        }
        media = MediaFileUpload(BACKUP_FILE, mimetype="application/octet-stream")

        # Search for an existing file with the same name in the specified folder
        query = f"'{BACKUP_FOLDER}' in parents and name='{BACKUP_FILE_NAME}' and trashed=false"
        response = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = response.get("files", [])

        if files:
            # Update the existing file (this keeps version history)
            file_id = files[0]["id"]
            drive_service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            print(f"Updated existing backup file in Google Drive: {file_id}")
        else:
            # Create a new file
            drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()
            print("Uploaded new backup file to Google Drive.")
    except Exception as e:
        print(f"Error uploading backup to Google Drive: {e}")
        sys.exit(1)

def restore_backup_to_local_db():
    print("Restoring backup to local PostgreSQL database for verification...")
    # Drop temp_db if it exists
    try:
        subprocess.run(["dropdb", TEMP_DB_NAME], check=True)
        print(f"Dropped existing database '{TEMP_DB_NAME}'.")
    except subprocess.CalledProcessError:
        print(f"Database '{TEMP_DB_NAME}' does not exist, skipping drop.")

    # Create temp_db
    try:
        subprocess.run(["createdb", TEMP_DB_NAME], check=True)
        print(f"Database '{TEMP_DB_NAME}' created.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating database '{TEMP_DB_NAME}': {e}")
        sys.exit(1)

    # Restore the backup to temp_db
    try:
        subprocess.run(
            ["pg_restore", "--clean", "--if-exists", "--no-owner", "-d", TEMP_DB_NAME, BACKUP_FILE],
            check=True
        )
        print(f"Backup restored to '{TEMP_DB_NAME}' successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error restoring backup to '{TEMP_DB_NAME}': {e}")
        sys.exit(1)

def verify_data_in_local_db():
    print("Verifying data in local PostgreSQL database...")
    try:
        # Create an engine and session for temp_db
        engine = create_engine(TEMP_DB_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Get the inspector for the database
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        if not all_tables:
            print("No tables found in the database.")
            return

        print(f"Database '{TEMP_DB_NAME}' found with {len(all_tables)} tables.")

        # User-defined variables
        TABLE_TO_OUTPUT = 'all'  # Set to 'all' or specific table name
        NUM_ROWS_TO_OUTPUT = '1'  # Set to 'all' or integer number of rows as a string

        # Determine which tables to process
        if TABLE_TO_OUTPUT.lower() == 'all':
            tables_to_process = all_tables
        else:
            if TABLE_TO_OUTPUT in all_tables:
                tables_to_process = [TABLE_TO_OUTPUT]
            else:
                print(f"Table '{TABLE_TO_OUTPUT}' not found in the database.")
                return

        # Create a MetaData object for reflection
        metadata = MetaData()
        metadata.reflect(bind=engine, only=tables_to_process)

        for table_name in tables_to_process:
            print(f"\nFirst {NUM_ROWS_TO_OUTPUT} rows for '{table_name}' table:")
            # Reflect the table
            try:
                table = Table(table_name, metadata, autoload_with=engine)
            except Exception as e:
                print(f"Error reflecting table '{table_name}': {e}")
                continue

            # Get column names
            columns = [str(column.name) for column in table.columns]
            # Print column headers in CSV format
            print(", ".join(columns))

            # Build a select query
            stmt = select(table)
            if NUM_ROWS_TO_OUTPUT.lower() != 'all':
                try:
                    limit = int(NUM_ROWS_TO_OUTPUT)
                    stmt = stmt.limit(limit)
                except ValueError:
                    print(f"Invalid number of rows: {NUM_ROWS_TO_OUTPUT}")
                    return

            # Execute the query
            try:
                result = session.execute(stmt)
                rows = result.fetchall()
                if not rows:
                    print("No entries found.")
                    continue

                # Access row data using the mapping interface
                for row in rows:
                    row_mapping = row._mapping
                    row_data = [str(row_mapping.get(col, '')) for col in columns]
                    print(", ".join(row_data))
            except Exception as e:
                print(f"Error querying table '{table_name}': {e}")
                continue

        # Close the session
        session.close()
    except Exception as e:
        print(f"Error during verification: {e}")
        sys.exit(1)

def cleanup_temp_db():
    """Clean up the temporary database."""
    print(f"Cleaning up local database '{TEMP_DB_NAME}'...")
    try:
        # Terminate all active connections to the database
        subprocess.run([
            "psql", "-d", "postgres", "-c",
            f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
            f"FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{TEMP_DB_NAME}' "
            f"AND pid <> pg_backend_pid();"
        ], check=True)
        print(f"All connections to '{TEMP_DB_NAME}' terminated.")

        # Drop the database
        subprocess.run(["dropdb", TEMP_DB_NAME], check=True)
        print(f"Temporary database '{TEMP_DB_NAME}' dropped.")
    except subprocess.CalledProcessError as e:
        print(f"Error dropping temporary database '{TEMP_DB_NAME}': {e}")

if __name__ == "__main__":
    backup_database()
    upload_to_google_drive()
    restore_backup_to_local_db()
    verify_data_in_local_db()
    cleanup_temp_db()