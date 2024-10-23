import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Now, you can import app and models after sys.path is correctly set
from app import app, db
from models import Costume

def fetch_costume_data(app_context):
    with app_context:
        print("Fetching and updating Costume Pokémon data...")

        url = "https://www.eurogamer.net/pokemon-go-event-costume-pokemon-party-hat-flower-crown-7002"
        start_time = time.time()
        print(f"Fetching data from {url}...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Fetched data in {time.time() - start_time:.2f} seconds")

        # Parse the HTML and extract costume Pokémon data
        tables = soup.find_all('table')
        total_costumes = 0
        costumes_data = []

        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip the header row
            total_costumes += len(rows)
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 2:
                    name = columns[0].get_text(strip=True)
                    first_appearance = columns[1].get_text(strip=True)
                    costume_type = "Costume" if 'costume' in name.lower() else "Unknown"
                    costumes_data.append((name, costume_type, first_appearance))

        count_inserted, count_updated, count_skipped = 0, 0, 0

        for idx, (name, costume, first_appearance) in enumerate(costumes_data):
            # Check if the costume entry already exists in the database
            existing_costume = Costume.query.filter_by(name=name).first()

            if existing_costume:
                if existing_costume.costume != costume or existing_costume.first_appearance != first_appearance:
                    existing_costume.costume = costume
                    existing_costume.first_appearance = first_appearance
                    db.session.commit()
                    count_updated += 1
                else:
                    count_skipped += 1
            else:
                new_costume = Costume(name=name, costume=costume, first_appearance=first_appearance)
                db.session.add(new_costume)
                db.session.commit()
                count_inserted += 1

            # Log progress every 10 entries
            if idx % 10 == 0:
                print(f"Processing Costume {idx + 1}/{total_costumes}...")

        print(f"Finished processing {total_costumes} Costume Pokémon.")
        print(f"Total Costumes added: {count_inserted}")
        print(f"Total Costumes updated: {count_updated}")
        print(f"Total Costumes skipped: {count_skipped}")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        fetch_costume_data(app.app_context())