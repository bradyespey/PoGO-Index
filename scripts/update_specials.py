# scripts/update_specials.py

import os
import sys
from pathlib import Path
import requests
import time

# Add the project root directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Now, you can import app and models after sys.path is correctly set
from app import app, db
from models import SpecialsPokemon

def fetch_and_update_specials(app_context):
    with app_context:
        print("Fetching and updating Special Pokémon data...")

        url = "https://gist.githubusercontent.com/Lusamine/a8604135b89dcfa840c61900c43df569/raw/7cdd446d7d13c9ea8cd385d630b29ceb550a1009/SV%25203.0.1%2520Legendary,%2520Mythical,%2520Sublegendary,%2520Ultra%2520Beast,%2520Paradox%2520Lists"
        start_time = time.time()
        print(f"Fetching data from {url}...")
        response = requests.get(url)
        raw_data = response.text
        print(f"Fetched data in {time.time() - start_time:.2f} seconds")

        # Parse the raw data
        categories = raw_data.split("\n\n")
        total_categories = len(categories)
        print(f"Found {total_categories} categories in the Special Pokémon data.")

        count_inserted, count_skipped = 0, 0

        for idx, category in enumerate(categories):
            lines = category.strip().split("\n")
            if not lines:
                continue

            type_ = lines[0].strip()
            if type_ == "Sublegend":
                type_ = "Legendary"

            for line in lines[1:]:
                if not line or ":" not in line:
                    continue

                dex_number = int(line.split(":")[0].strip().replace("#", ""))
                name = line.split(":")[1].split("--")[0].strip()

                # Check if the Special entry already exists
                special_pokemon = SpecialsPokemon.query.filter_by(dex_number=dex_number, name=name).first()

                if special_pokemon:
                    count_skipped += 1
                else:
                    # Insert new Special Pokémon
                    print(f"Inserting new special Pokémon {name} with dex number {dex_number}")
                    new_special = SpecialsPokemon(dex_number=dex_number, name=name, type=type_)
                    db.session.add(new_special)
                    db.session.commit()
                    count_inserted += 1

            # Log progress for each category processed
            print(f"Processed category {idx + 1}/{total_categories}: {type_}")

        # Final output
        print("Finished processing Special Pokémon")
        print(f"Total Special Pokémon added: {count_inserted}")
        print(f"Total Shiny Pokémon skipped: {count_skipped}")

if __name__ == "__main__":
    with app.app_context():
        fetch_and_update_specials(app.app_context())
