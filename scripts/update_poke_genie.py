# scripts/update_poke_genie.py

import os
import sys
from pathlib import Path
import csv
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Add the project root directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the app and database models
from app import app, db
from models import PokeGenieEntry, User

# Google API and folder ID configurations
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1--T8Abai5H-b8vY_OVAVHKdA4NXC50rS'

SERVICE_ACCOUNT_INFO = {
    "type": os.getenv('SERVICE_ACCOUNT_TYPE'),
    "project_id": os.getenv('SERVICE_ACCOUNT_PROJECT_ID'),
    "private_key_id": os.getenv('SERVICE_ACCOUNT_PRIVATE_KEY_ID'),
    "private_key": os.getenv('SERVICE_ACCOUNT_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.getenv('SERVICE_ACCOUNT_CLIENT_EMAIL'),
    "client_id": os.getenv('SERVICE_ACCOUNT_CLIENT_ID'),
    "auth_uri": os.getenv('SERVICE_ACCOUNT_AUTH_URI'),
    "token_uri": os.getenv('SERVICE_ACCOUNT_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.getenv('SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL'),
    "client_x509_cert_url": os.getenv('SERVICE_ACCOUNT_CLIENT_CERT_URL'),
}

# Create Google API credentials
creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

def get_or_create_default_user():
    # Check if a user with google_id 'default_google_id' already exists
    default_user = User.query.filter_by(google_id='default_google_id').first()
    if default_user:
        return default_user.id  # Return the existing user's ID if found

    # Create a new default user if it doesn't exist
    new_user = User(
        google_id='default_google_id',
        name='Default User',
        email='default@example.com'
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user.id  # Return the new user's ID

def download_latest_csv_from_drive():
    """Download the latest CSV file from Google Drive."""
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

def sanitize_numeric(value):
    """Convert strings like '2.29kg' to floats by removing non-numeric characters."""
    try:
        clean_value = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        return float(clean_value) if clean_value else None
    except ValueError:
        return None

def sanitize_percentage(value):
    """Convert percentage strings like '77.70%' to floats."""
    try:
        return float(value.replace('%', '').strip()) if value else None
    except ValueError:
        return None

def import_poke_genie_data(app_context):
    """Process and insert the CSV data into the Poke Genie table."""
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

            user_id = get_or_create_default_user()

            count_inserted, count_skipped = 0, 0

            for idx, row in enumerate(reader):
                index = int(row[0])
                name = row[1]
                form = row[2]
                pokemon_number = int(row[3])  # Dex number
                gender = row[4]
                cp = int(row[5]) if row[5] else None
                hp = int(row[6]) if row[6] else None
                atk_iv = int(row[7]) if row[7] else None
                def_iv = int(row[8]) if row[8] else None
                sta_iv = int(row[9]) if row[9] else None
                iv_avg = float(row[10]) if row[10] else None
                level_min = float(row[11]) if row[11] else None
                level_max = float(row[12]) if row[12] else None
                quick_move = row[13]
                charge_move = row[14]
                charge_move_2 = row[15]
                scan_date = row[16]
                original_scan_date = row[17]
                catch_date = row[18]
                weight = sanitize_numeric(row[19])
                height = sanitize_numeric(row[20])
                lucky = int(row[21]) if row[21] else None
                shadow_purified = int(row[22]) if row[22] else None
                favorite = int(row[23]) if row[23] else None
                dust = int(row[24]) if row[24] else None
                rank_g_pct = sanitize_percentage(row[25])
                rank_g_num = int(row[26]) if row[26] else None
                stat_prod_g = sanitize_numeric(row[27])
                dust_cost_g = int(row[28]) if row[28] else None
                candy_cost_g = int(row[29]) if row[29] else None
                name_g = row[30]
                form_g = row[31]
                sha_pur_g = int(row[32]) if row[32] else None
                rank_u_pct = sanitize_percentage(row[33])
                rank_u_num = int(row[34]) if row[34] else None
                stat_prod_u = sanitize_numeric(row[35])
                dust_cost_u = int(row[36]) if row[36] else None
                candy_cost_u = int(row[37]) if row[37] else None
                name_u = row[38]
                form_u = row[39]
                sha_pur_u = int(row[40]) if row[40] else None
                rank_l_pct = sanitize_percentage(row[41])
                rank_l_num = int(row[42]) if row[42] else None
                stat_prod_l = sanitize_numeric(row[43])
                dust_cost_l = int(row[44]) if row[44] else None
                candy_cost_l = int(row[45]) if row[45] else None
                name_l = row[46]
                form_l = row[47]
                sha_pur_l = int(row[48]) if row[48] else None
                marked_for_pvp = int(row[49]) if row[49] else None

                # Check for existing entry to avoid duplicates
                existing_entry = PokeGenieEntry.query.filter_by(index=index).first()

                if existing_entry:
                    count_skipped += 1
                else:
                    print(f"Inserting new Poke Genie entry for Pokémon {name} with dex number {pokemon_number}")
                    # Add a new entry with all fields populated
                    new_entry = PokeGenieEntry(
                        index=index,
                        name=name,
                        form=form,
                        pokemon_number=pokemon_number,
                        gender=gender,
                        cp=cp,
                        hp=hp,
                        atk_iv=atk_iv,
                        def_iv=def_iv,
                        sta_iv=sta_iv,
                        iv_avg=iv_avg,
                        level_min=level_min,
                        level_max=level_max,
                        quick_move=quick_move,
                        charge_move=charge_move,
                        charge_move_2=charge_move_2,
                        scan_date=scan_date,
                        original_scan_date=original_scan_date,
                        catch_date=catch_date,
                        weight=weight,
                        height=height,
                        lucky=lucky,
                        shadow_purified=shadow_purified,
                        favorite=favorite,
                        dust=dust,
                        rank_g_pct=rank_g_pct,
                        rank_g_num=rank_g_num,
                        stat_prod_g=stat_prod_g,
                        dust_cost_g=dust_cost_g,
                        candy_cost_g=candy_cost_g,
                        name_g=name_g,
                        form_g=form_g,
                        sha_pur_g=sha_pur_g,
                        rank_u_pct=rank_u_pct,
                        rank_u_num=rank_u_num,
                        stat_prod_u=stat_prod_u,
                        dust_cost_u=dust_cost_u,
                        candy_cost_u=candy_cost_u,
                        name_u=name_u,
                        form_u=form_u,
                        sha_pur_u=sha_pur_u,
                        rank_l_pct=rank_l_pct,
                        rank_l_num=rank_l_num,
                        stat_prod_l=stat_prod_l,
                        dust_cost_l=dust_cost_l,
                        candy_cost_l=candy_cost_l,
                        name_l=name_l,
                        form_l=form_l,
                        sha_pur_l=sha_pur_l,
                        marked_for_pvp=marked_for_pvp
                    )
                    db.session.add(new_entry)
                    db.session.commit()
                    count_inserted += 1

            print(f"Finished processing {total_entries} Poke Genie entries")
            print(f"Total entries added: {count_inserted}")
            print(f"Total entries skipped: {count_skipped}")

if __name__ == "__main__":
    with app.app_context():
        import_poke_genie_data(app.app_context())
