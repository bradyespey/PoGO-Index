import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time

# Add the project root directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Now, you can import app and models after sys.path is correctly set
from app import app, db
from models import Costume

# Helper functions to clean and process HTML data
def decode_html(html):
    """Helper function to decode HTML entities like &eacute;."""
    return (html.replace('&amp;', '&')
                .replace('&lt;', '<')
                .replace('&gt;', '>')
                .replace('&quot;', '"')
                .replace('&#39;', "'")
                .replace('&eacute;', 'é')
                .replace('&uacute;', 'ú')
                .replace('&Eacute;', 'É')
                .replace('&Uacute;', 'Ú'))

def extract_costume_data(html):
    """Parse the HTML and extract costume Pokémon data."""
    soup = BeautifulSoup(html, 'html.parser')  # Convert HTML content to a BeautifulSoup object

    # Find all tables that might contain costume Pokémon data
    tables = soup.find_all('table')

    # Placeholder list for the parsed data (dex_number, name, costume, first appearance)
    costumes_data = []

    # Loop through each table (assuming that costume data is within table rows)
    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip the first row (header)
            columns = row.find_all('td')

            # Ensure the row has enough columns to be valid
            if len(columns) >= 2:
                name = decode_html(columns[0].get_text(strip=True))
                first_appearance = decode_html(columns[1].get_text(strip=True))

                # Using placeholder dex_number since Eurogamer page doesn’t seem to have dex numbers
                dex_number = None  # You'll need a lookup mechanism to map name -> dex number

                # Match the name with the costume if possible
                costume_type = "Unknown"
                if 'costume' in name.lower():
                    costume_type = 'Costume'
                elif 'flower crown' in name.lower():
                    costume_type = 'Flower Crown'
                elif 'party hat' in name.lower():
                    costume_type = 'Party Hat'

                # Append the parsed data
                costumes_data.append((dex_number, name, costume_type, first_appearance))

    return costumes_data

def fetch_costume_data(app_context):
    with app_context:
        print("Fetching and updating Costume Pokémon data...")

        url = "https://www.eurogamer.net/pokemon-go-event-costume-pokemon-party-hat-flower-crown-7002"
        start_time = time.time()
        print(f"Fetching data from {url}...")
        response = requests.get(url)
        soup = response.text  # Use response.text, which is the raw HTML content
        print(f"Fetched data in {time.time() - start_time:.2f} seconds")

        # Parse the HTML and extract costume Pokémon data
        costumes_data = extract_costume_data(soup)

        count_inserted, count_updated, count_skipped = 0, 0, 0

        for idx, (dex_number, name, costume, first_appearance) in enumerate(costumes_data):
            # Check if the costume entry already exists in the database
            existing_costume = Costume.query.filter_by(name=name).first()

            if existing_costume:
                # Update the existing costume entry if data has changed
                if existing_costume.costume != costume or existing_costume.first_appearance != first_appearance:
                    existing_costume.costume = costume
                    existing_costume.first_appearance = first_appearance
                    db.session.commit()
                    count_updated += 1
                else:
                    count_skipped += 1
            else:
                # Insert a new costume entry
                new_costume = Costume(dex_number=dex_number, name=name, costume=costume, first_appearance=first_appearance)
                db.session.add(new_costume)
                db.session.commit()
                count_inserted += 1

            # Log progress every 10 entries
            if idx % 10 == 0:
                print(f"Processing Costume {idx + 1}/{len(costumes_data)}...")

        # Output the results
        print(f"Finished processing {len(costumes_data)} Costume Pokémon.")
        print(f"Total Costumes added: {count_inserted}")
        print(f"Total Costumes updated: {count_updated}")
        print(f"Total Costumes skipped: {count_skipped}")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        fetch_costume_data(app.app_context())